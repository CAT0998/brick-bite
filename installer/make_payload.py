# -*- coding: utf-8 -*-
"""Build an installer payload directory from a compiled OrcaSlicer build.

Usage: python make_payload.py <build_dir> <payload_dir> <version_label>
"""
import hashlib, json, shutil, sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 1
    src, dst, label = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    exe_names = ("orca-slicer.exe", "bambu-studio.exe")
    if not any((src / n).exists() for n in exe_names):
        print(f"error: {src} does not contain any of {exe_names}")
        return 2
    if dst.exists():
        shutil.rmtree(dst)
    print(f"copying {src} -> {dst} ...")
    shutil.copytree(src, dst)

    files = []
    for p in sorted(dst.rglob("*")):
        if p.is_file() and p.name != "manifest.json":
            rel = p.relative_to(dst).as_posix()
            files.append({"path": rel, "sha256": sha256(p), "size": p.stat().st_size})
    manifest = {"version": label, "files": files}
    (dst / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"manifest: {len(files)} files, version {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
