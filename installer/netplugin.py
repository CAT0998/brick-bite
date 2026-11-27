# -*- coding: utf-8 -*-
"""Put the Bambu network plug-in where a Brick Bite Bambu Studio build looks for it.

Why this is needed
------------------
Our Bambu Studio builds are compiled with ``BBL_INTERNAL_TESTING=1`` (it is the
default in ``version.inc`` when the tree is not a tagged Bambu release).  That
switch makes ``GUI_App::init_app_config()`` append ``"Internal"`` to the data
directory::

    #if BBL_INTERNAL_TESTING
        data_dir += BBL_INTERNAL_TESTING == 1 ? "Internal" : "Beta";
    #endif

so the application reads/writes ``%APPDATA%\\BambuStudioInternal`` while the
official release uses ``%APPDATA%\\BambuStudio``.  The Bambu network plug-in
(``bambu_networking.dll`` + 6 companion DLLs) is installed into
``<data dir>\\plugins``, therefore a patched build finds no plug-in at all, shows
"请在登陆前安装网络插件" / "Please install the network plug-in before logging
in", and the built-in downloader fails to fetch it (that download path is also
broken in these builds).

This module installs the plug-in directly:

1. ask Bambu's resource API which plug-in matches the application version,
2. download that package and unpack the DLLs into ``<data dir>\\plugins``,
3. fall back to copying the plug-in from an official installation when offline.

Running it twice is harmless: an already installed plug-in of the same version is
left untouched (a small marker file remembers what was installed).
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

# Bambu Studio builds produced by this project are "internal testing" builds, so
# the app looks in BambuStudioInternal.  See the module docstring.
DATA_DIR_NAME = "BambuStudioInternal"
OFFICIAL_DATA_DIR_NAME = "BambuStudio"

API_HOSTS = ("https://api.bambulab.com", "https://api.bambulab.cn")
API_PATH = "/v1/iot-service/api/slicer/resource"
USER_AGENT = "BambuStudio/%s"
MARKER_NAME = ".brickbite_netplugin.json"
PLUGIN_DLLS = (
    "bambu_networking.dll",
    "BambuSource.dll",
    "agora_rtc_sdk.dll",
    "libagora-ffmpeg.dll",
    "libagora-soundtouch.dll",
    "libaosl.dll",
    "live555.dll",
)


def _noop(_msg):
    pass


def app_version(app_dir: Path) -> str:
    """Best-effort read of the application version (e.g. "02.09.02.62")."""
    exe = Path(app_dir) / "bambu-studio.exe"
    if not exe.exists():
        return ""
    for source in _version_candidates(exe):
        if source:
            return source
    return ""


def _version_candidates(exe: Path):
    # 1) Windows version resource, cheap and reliable for our builds
    try:
        import ctypes
        from ctypes import wintypes

        ver = ctypes.WinDLL("version")
        size = ver.GetFileVersionInfoSizeW(str(exe), None)
        if size:
            buf = ctypes.create_string_buffer(size)
            if ver.GetFileVersionInfoW(str(exe), 0, size, buf):
                r = wintypes.LPVOID()
                ln = wintypes.UINT()
                if ver.VerQueryValueW(buf, "\\", ctypes.byref(r), ctypes.byref(ln)):
                    class FixedFileInfo(ctypes.Structure):
                        _fields_ = [
                            ("dwSignature", wintypes.DWORD),
                            ("dwStrucVersion", wintypes.DWORD),
                            ("dwFileVersionMS", wintypes.DWORD),
                            ("dwFileVersionLS", wintypes.DWORD),
                            ("dwProductVersionMS", wintypes.DWORD),
                            ("dwProductVersionLS", wintypes.DWORD),
                            ("dwFileFlagsMask", wintypes.DWORD),
                            ("dwFileFlags", wintypes.DWORD),
                            ("dwFileOS", wintypes.DWORD),
                            ("dwFileType", wintypes.DWORD),
                            ("dwFileSubtype", wintypes.DWORD),
                            ("dwFileDateMS", wintypes.DWORD),
                            ("dwFileDateLS", wintypes.DWORD),
                        ]

                    ff = ctypes.cast(r, ctypes.POINTER(FixedFileInfo)).contents
                    ms, ls = ff.dwFileVersionMS, ff.dwFileVersionLS
                    yield "%02d.%02d.%02d.%02d" % (
                        (ms >> 16) & 0xFFFF,
                        ms & 0xFFFF,
                        (ls >> 16) & 0xFFFF,
                        ls & 0xFFFF,
                    )
                    return
    except Exception:
        pass
    yield ""


def series_of(version: str) -> str:
    """"02.09.02.62" -> "02.09.02" (the plug-in series the API keys on)."""
    parts = [p for p in (version or "").split(".") if p]
    if len(parts) >= 3:
        return ".".join(parts[:3])
    return ""


def fetch_plugin_info(series: str, timeout: int = 25) -> dict | None:
    """Ask the resource API which network plug-in matches this series."""
    if not series:
        return None
    query = "?slicer/plugins/cloud=%s.00" % series
    headers = {"User-Agent": USER_AGENT % (series + ".00")}
    for host in API_HOSTS:
        url = host + API_PATH + query
        try:
            req = urllib.request.Request(url, headers=headers)
            body = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
            data = json.loads(body)
        except Exception:
            continue
        for res in data.get("resources") or []:
            if res.get("type") == "slicer/plugins/cloud" and res.get("url"):
                return {"version": res.get("version") or series, "url": res["url"]}
    return None


def download_plugin(url: str, dest: Path, timeout: int = 60, attempts: int = 4, log=_noop) -> Path:
    """Download *url* to *dest*, resuming after a stalled or dropped connection.

    The Bambu CDN occasionally stalls mid-transfer on this network, so every
    successful chunk is kept and the next attempt asks for the remaining bytes
    with a Range header.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(1, attempts + 1):
        got = dest.stat().st_size if dest.exists() else 0
        headers = {"User-Agent": USER_AGENT % "02.09.02.00", "Accept": "*/*"}
        if got:
            headers["Range"] = "bytes=%d-" % got
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if got and getattr(resp, "status", 200) == 200:
                    got = 0  # server ignored the Range header, start over
                expected = resp.headers.get("Content-Length")
                expected = int(expected) + got if expected else None
                mode = "ab" if got else "wb"
                with open(dest, mode) as f:
                    while True:
                        chunk = resp.read(1 << 20)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
            if expected is None or dest.stat().st_size >= expected:
                return dest
            last_error = "incomplete (%d/%s bytes)" % (dest.stat().st_size, expected)
        except Exception as exc:  # noqa: BLE001 - retried with Range
            last_error = "%s: %s" % (type(exc).__name__, exc)
            log("download attempt %d/%d failed (%s)" % (attempt, attempts, last_error))
    raise RuntimeError("could not download %s (%s)" % (url, last_error))


def _read_marker(plugins: Path) -> dict:
    try:
        return json.loads((plugins / MARKER_NAME).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _install_from_zip(zip_path: Path, plugins: Path, version: str) -> int:
    plugins.mkdir(parents=True, exist_ok=True)
    written = 0
    with zipfile.ZipFile(zip_path) as z:
        names = {n.split("/")[-1].lower(): n for n in z.namelist() if not n.endswith("/")}
        for dll in PLUGIN_DLLS:
            name = names.get(dll.lower())
            if not name:
                continue
            dst = plugins / dll
            if dst.exists():
                try:
                    shutil.copy2(dst, dst.with_suffix(dst.suffix + ".brickbite.bak"))
                except OSError:
                    pass
            (plugins / dll).write_bytes(z.read(name))
            written += 1
    (plugins / MARKER_NAME).write_text(
        json.dumps({"version": version, "source": "bambu-resource-api"}, indent=1),
        encoding="utf-8",
    )
    return written


def _install_from_official(official_plugins: Path, plugins: Path, version: str) -> int:
    if not (official_plugins / "bambu_networking.dll").exists():
        return 0
    plugins.mkdir(parents=True, exist_ok=True)
    written = 0
    for dll in PLUGIN_DLLS:
        src = official_plugins / dll
        if not src.exists():
            continue
        dst = plugins / dll
        if dst.exists():
            try:
                shutil.copy2(dst, dst.with_suffix(dst.suffix + ".brickbite.bak"))
            except OSError:
                pass
        shutil.copy2(src, dst)
        written += 1
    (plugins / MARKER_NAME).write_text(
        json.dumps({"version": version or "unknown", "source": "official-installation"}, indent=1),
        encoding="utf-8",
    )
    return written


def ensure_network_plugin(app_dir: Path, data_root: Path | None = None, log=_noop) -> str:
    """Install the Bambu network plug-in for the build in *app_dir*.

    Returns one of: "ok" (installed), "present" (already there), "missing-app",
    "no-source" (nothing could be fetched), "error".
    """
    app_dir = Path(app_dir)
    if not (app_dir / "bambu-studio.exe").exists():
        return "missing-app"

    data_root = Path(data_root) if data_root else Path(os.environ.get("APPDATA", ""))
    data_dir = data_root / DATA_DIR_NAME
    plugins = data_dir / "plugins"

    version = app_version(app_dir)
    series = series_of(version)
    marker = _read_marker(plugins)
    if (plugins / "bambu_networking.dll").exists() and marker.get("version"):
        log("network plug-in already installed (%s)" % marker.get("version"))
        return "present"

    info = fetch_plugin_info(series) if series else None
    if info:
        target_version = info["version"]
        if marker.get("version") == target_version and (plugins / "bambu_networking.dll").exists():
            return "present"
        log("downloading network plug-in %s for %s" % (target_version, version or series))
        tmpdir = Path(tempfile.mkdtemp(prefix="brickbite-netplugin-"))
        try:
            zip_path = download_plugin(info["url"], tmpdir / ("win_%s.zip" % target_version))
            count = _install_from_zip(zip_path, plugins, target_version)
        except Exception as exc:  # noqa: BLE001 - fall through to offline copy
            log("download failed (%s), trying an existing installation" % type(exc).__name__)
            count = 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        if count:
            log("network plug-in %s installed into %s" % (target_version, plugins))
            return "ok"

    official = data_root / OFFICIAL_DATA_DIR_NAME / "plugins"
    count = _install_from_official(official, plugins, series)
    if count:
        log("copied network plug-in from the official installation into %s" % plugins)
        return "ok"

    log("could not obtain the network plug-in (no download, no official installation)")
    return "no-source"


if __name__ == "__main__":  # manual repair: python netplugin.py <app dir>
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    print(ensure_network_plugin(target, log=lambda m: print(">", m)))
