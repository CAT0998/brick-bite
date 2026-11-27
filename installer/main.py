#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brick Bite installer (PySide6).

Installs the Brick Bite patched OrcaSlicer into an existing installation by
replacing only the files whose hash differs. Backups are written as *.brickbite.bak.
"""
import json, os, sys, hashlib, shutil, subprocess, zipfile, traceback
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from i18n import T, agreement, set_language, LANG as _LANG
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QTextBrowser, QCheckBox, QRadioButton, QLineEdit, QFileDialog,
    QProgressBar, QPlainTextEdit, QMessageBox, QButtonGroup, QComboBox
)

APP_NAME = T("app_name")
_WIN = None
EXE_CANDIDATES = ("orca-slicer.exe", "bambu-studio.exe")
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ASSETS = BASE / "assets"

def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def read_version(exe: Path):
    try:
        cmd = ["powershell", "-NoProfile", "-Command",
               f"(Get-Item -LiteralPath '{exe}').VersionInfo.FileVersion"]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        v = (out.stdout or "").strip()
        return v or None
    except Exception:
        return None

def detect_installations(kind=None):
    wanted = {"orca": "orca-slicer.exe", "bambu": "bambu-studio.exe"}.get(kind or "", None)
    candidates = []
    # registry uninstall entries
    try:
        import winreg
        for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for sub in (r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
                        r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"):
                try:
                    key = winreg.OpenKey(root, sub)
                except OSError:
                    continue
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        name = winreg.EnumKey(key, i)
                        k = winreg.OpenKey(key, name)
                        display = winreg.QueryValueEx(k, "DisplayName")[0]
                        loc = winreg.QueryValueEx(k, "InstallLocation")[0]
                        if loc and ("orca" in str(display).lower() or "bambu" in str(display).lower()):
                            candidates.append(Path(loc))
                    except OSError:
                        continue
    except Exception:
        pass
    # common paths
    for p in (r"C:\Program Files\OrcaSlicer", r"C:\Program Files (x86)\OrcaSlicer",
              str(Path.home() / "AppData/Local/Programs/OrcaSlicer"),
              "D:\\OrcaSlicer", "E:\\OrcaSlicer",
              r"C:\Program Files\Bambu Studio", r"C:\Program Files (x86)\Bambu Studio",
              str(Path.home() / "AppData/Local/Programs/Bambu Studio"),
              "D:\\BambuStudio", "E:\\BambuStudio"):
        candidates.append(Path(p))
    # sibling folders next to an existing install (E:\BambuStudio-2.9.2-BrickBite ...)
    for parent in ("C:\\", "D:\\", "E:\\", "F:\\"):
        try:
            for child in Path(parent).iterdir():
                name = child.name.lower()
                if child.is_dir() and ("bambustudio" in name or "orcaslicer" in name):
                    candidates.append(child)
        except OSError:
            continue
    seen, out = set(), []
    for c in candidates:
        try:
            hit = (c / wanted).exists() if wanted else any((c / name).exists() for name in EXE_CANDIDATES)
            if hit and str(c).lower() not in seen:
                seen.add(str(c).lower()); out.append(c)
        except Exception:
            pass
    return out

def make_shortcut(target_exe: Path, name=None):
    name = name or T("shortcut_name")
    desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
    lnk = desktop / f"{name}.lnk"
    ps = f'''$ws=New-Object -ComObject WScript.Shell
$s=$ws.CreateShortcut("{lnk}")
$s.TargetPath="{target_exe}"
$s.WorkingDirectory="{target_exe.parent}"
$s.IconLocation="{target_exe},0"
$s.Save()'''
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return lnk

class Worker(QThread):
    progress = Signal(int, str)
    log = Signal(str)
    done = Signal(bool, str)

    def __init__(self, target: Path, payload_dir: Path, manifest: dict, restore=False):
        super().__init__()
        self.target, self.payload, self.manifest, self.restore = target, payload_dir, manifest, restore

    def run(self):
        try:
            files = self.manifest.get("files", [])
            total = len(files) or 1
            copied = skipped = 0
            last_pct = -1
            for i, item in enumerate(files):
                rel, h = item["path"], item["sha256"]
                src = self.payload / rel
                dst = self.target / rel
                pct = int((i + 1) * 100 / total)
                if self.restore:
                    bak = dst.with_suffix(dst.suffix + ".brickbite.bak")
                    if bak.exists():
                        shutil.copy2(bak, dst); self.log.emit(T("log_restore", rel=rel))
                    if pct != last_pct:
                        last_pct = pct
                        self.progress.emit(pct, T("log_restore", rel=rel))
                    continue
                if not src.exists():
                    continue
                if dst.exists() and sha256(dst) == h:
                    skipped += 1
                    # Only nudge the bar once per percent: one signal per file made
                    # the window look hung while thousands sat in the event queue.
                    if pct != last_pct:
                        last_pct = pct
                        self.progress.emit(pct, T("log_skip", rel=rel))
                    continue
                if dst.exists():
                    shutil.copy2(dst, dst.with_suffix(dst.suffix + ".brickbite.bak"))
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
                last_pct = pct
                self.log.emit(T("log_replace", rel=rel))
                self.progress.emit(pct, T("log_replace", rel=rel))
            message = T("log_summary", copied=copied, skipped=skipped) + self.install_net_plugin()
            self.done.emit(True, message)
        except Exception as exc:
            self.done.emit(False, f"{exc}\n{traceback.format_exc()}")

    def install_net_plugin(self):
        """Bambu builds keep their data in %APPDATA%\\BambuStudioInternal, so the
        plug-in installed by the official release is invisible to them.  Fetch it
        on this worker thread (never the GUI thread) right after the files land."""
        if not (self.payload / "bambu-studio.exe").exists():
            return ""
        try:
            from netplugin import ensure_network_plugin
        except Exception as exc:
            self.log.emit("network plug-in module missing: %r" % (exc,))
            return "\n" + T("net_plugin_warn")
        try:
            result = ensure_network_plugin(self.target, log=self.log.emit)
        except Exception as exc:
            self.log.emit("network plug-in step failed: %r" % (exc,))
            return "\n" + T("net_plugin_warn")
        if result in ("ok", "present"):
            return "\n" + T("net_plugin_ok")
        if result == "missing-app":
            return ""
        return "\n" + T("net_plugin_warn")

QSS = """
* { font-family: "Microsoft YaHei", "Segoe UI"; }
QMainWindow, QWidget#root { background:#171d31; }
QWidget#left { background:#131a2e; border-right:1px solid #2a3352; }
QLabel#title { color:#e8ecff; font-size:24px; font-weight:700; }
QLabel#say { background:#1d2642; border:1px solid #2f3b63; border-radius:12px; color:#cdd6f7; padding:10px; font-size:13px; }
QLabel#muted { color:#93a0c8; font-size:12px; }
QLabel#credit { color:#7f8bb3; font-size:12px; }
QTextBrowser { background:#0f1526; border:1px solid #2a3352; border-radius:10px; color:#c6cff0; padding:8px; font-size:13px; }
QCheckBox, QRadioButton { color:#c6cff0; font-size:13px; }
QLineEdit { background:#0f1526; border:1px solid #2a3352; border-radius:8px; color:#e8ecff; padding:8px; }
QPushButton { background:#4d6bfe; color:white; border:none; border-radius:8px; padding:9px 20px; font-size:14px; }
QPushButton:disabled { background:#2b3557; color:#7d88ad; }
QPushButton#ghost { background:transparent; border:1px solid #2a3352; color:#93a0c8; }
QProgressBar { background:#0f1526; border:1px solid #2a3352; border-radius:8px; height:16px; text-align:center; color:#cdd6f7; }
QProgressBar::chunk { background:#4d6bfe; border-radius:7px; }
QPlainTextEdit { background:#0d1220; border:1px solid #2a3352; border-radius:8px; color:#8fa0cf; font-family:Consolas; font-size:12px; }
"""



class Installer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(T("app_name"))
        self.resize(900, 600)
        self.setStyleSheet(QSS)
        self.step = 0
        self.mode = "auto"
        self.path = "D:\\OrcaSlicer"
        self.worker = None
        self.failed = False
        self.manifest = self.load_manifest()
        self.build_ui()
        self.render()

    def on_lang_change(self, idx):
        code = self.lang_box.itemData(idx)
        if not code:
            return
        set_language(code)
        global _WIN
        _WIN = Installer()
        _WIN.show()
        self.close()

    def load_manifest(self):
        for cand in (app_dir() / "payload" / "manifest.json", app_dir() / "manifest.json"):
            if cand.exists():
                try:
                    return json.loads(cand.read_text(encoding="utf-8"))
                except Exception:
                    pass
        return {"files": []}

    def payload_dir(self):
        return app_dir() / "payload"

    def payload_kind(self):
        """Which slicer this installer carries: "bambu", "orca" or None."""
        payload = self.payload_dir()
        if (payload / "bambu-studio.exe").exists():
            return "bambu"
        if (payload / "orca-slicer.exe").exists():
            return "orca"
        return None

    def build_ui(self):
        root = QWidget(objectName="root")
        self.setCentralWidget(root)
        h = QHBoxLayout(root); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(0)

        left = QWidget(objectName="left"); left.setFixedWidth(280)
        lv = QVBoxLayout(left); lv.setContentsMargins(16, 18, 16, 16)
        pic = QLabel(); pic.setFixedSize(180, 180)
        img = ASSETS / "whale.png"
        if img.exists():
            pic.setPixmap(QPixmap(str(img)).scaled(180, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        pic.setStyleSheet("border-radius:20px; border:2px solid #2f3b63;")
        lv.addWidget(pic, 0, Qt.AlignHCenter)
        self.say = QLabel(objectName="say"); self.say.setWordWrap(True); self.say.setMinimumHeight(80)
        lv.addWidget(self.say)
        lv.addStretch(1)
        self.lang_box = QComboBox()
        self.lang_box.addItem("简体中文", "zh")
        self.lang_box.addItem("繁體中文", "tw")
        self.lang_box.addItem("English", "en")
        idx = self.lang_box.findData(_LANG)
        self.lang_box.setCurrentIndex(idx if idx >= 0 else 0)
        self.lang_box.currentIndexChanged.connect(self.on_lang_change)
        lv.addWidget(self.lang_box)
        foot = QLabel(T("credit"), objectName="credit"); foot.setWordWrap(True)
        foot.setAlignment(Qt.AlignHCenter); lv.addWidget(foot)
        h.addWidget(left)

        right = QWidget(); rv = QVBoxLayout(right); rv.setContentsMargins(26, 22, 26, 16)
        self.stack = QStackedWidget(); rv.addWidget(self.stack, 1)

        bar = QHBoxLayout()
        self.steps_lbl = QLabel(objectName="muted"); bar.addWidget(self.steps_lbl, 1)
        self.back_btn = QPushButton(T("btn_back"), objectName="ghost"); self.back_btn.clicked.connect(lambda: self.go(-1))
        self.next_btn = QPushButton(T("btn_next")); self.next_btn.clicked.connect(lambda: self.go(1))
        bar.addWidget(self.back_btn); bar.addWidget(self.next_btn)
        rv.addLayout(bar)
        h.addWidget(right, 1)

        # pages
        self.page_welcome = self.make_welcome()
        self.page_agree = self.make_agree()
        self.page_mode = self.make_mode()
        self.page_path = self.make_path()
        self.page_install = self.make_install()
        self.page_finish = self.make_finish()
        for p in (self.page_welcome, self.page_agree, self.page_mode, self.page_path, self.page_install, self.page_finish):
            self.stack.addWidget(p)

    def make_welcome(self):
        w = QWidget(); v = QVBoxLayout(w)
        t = QLabel(T("welcome_title"), objectName="title"); v.addWidget(t)
        v.addWidget(QLabel(T("welcome_sub"), objectName="muted"))
        body = QLabel(T("welcome_body"))
        body.setWordWrap(True); v.addWidget(body)
        v.addStretch(1)
        return w

    def make_agree(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.addWidget(QLabel(T("agree_title"), objectName="title"))
        tb = QTextBrowser(); tb.setPlainText(agreement()); v.addWidget(tb, 1)
        self.agree_box = QCheckBox(T("agree_check"))
        self.agree_box.stateChanged.connect(self.on_agree)
        v.addWidget(self.agree_box)
        return w

    def make_mode(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.addWidget(QLabel(T("mode_title"), objectName="title"))
        self.rb_auto = QRadioButton(T("mode_auto"))
        self.rb_manual = QRadioButton(T("mode_manual"))
        self.rb_auto.setChecked(True)
        g = QButtonGroup(w); g.addButton(self.rb_auto); g.addButton(self.rb_manual)
        self.rb_auto.toggled.connect(lambda on: on and self.set_mode("auto"))
        self.rb_manual.toggled.connect(lambda on: on and self.set_mode("manual"))
        v.addWidget(self.rb_auto); v.addWidget(self.rb_manual); v.addStretch(1)
        return w

    def make_path(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.addWidget(QLabel(T("path_title"), objectName="title"))
        self.path_hint = QLabel(objectName="muted"); v.addWidget(self.path_hint)
        row = QHBoxLayout()
        self.path_edit = QLineEdit(); row.addWidget(self.path_edit, 1)
        b = QPushButton(T("btn_browse"), objectName="ghost"); b.clicked.connect(self.browse)
        row.addWidget(b); v.addLayout(row)
        note = QLabel(T("path_note"))
        note.setWordWrap(True); v.addWidget(note)
        v.addStretch(1)
        return w

    def make_install(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.addWidget(QLabel(T("install_title"), objectName="title"))
        self.pbar = QProgressBar(); self.pbar.setRange(0, 100); v.addWidget(self.pbar)
        self.plabel = QLabel(T("install_preparing"), objectName="muted"); v.addWidget(self.plabel)
        self.plog = QPlainTextEdit(); self.plog.setReadOnly(True); v.addWidget(self.plog, 1)
        return w

    def make_finish(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.finish_title = QLabel(T("finish_title"), objectName="title"); v.addWidget(self.finish_title)
        self.finish_body = QLabel(); self.finish_body.setWordWrap(True); v.addWidget(self.finish_body)
        v.addStretch(1)
        return w

    def set_mode(self, m):
        self.mode = m

    def on_agree(self):
        self.next_btn.setEnabled(bool(self.agree_box.isChecked()) or self.step != 1)
        if self.step == 1:
            self.next_btn.setEnabled(bool(self.agree_box.isChecked()))

    def browse(self):
        d = QFileDialog.getExistingDirectory(self, T("browse_title"), self.path_edit.text())
        if d:
            self.path_edit.setText(d)

    def say_text(self, t):
        self.say.setText(t)

    def render(self):
        names = [T("step_welcome"), T("step_agree"), T("step_mode"), T("step_path"), T("step_install"), T("step_finish")]
        self.steps_lbl.setText("  ·  ".join(f"{i+1}. {n}" for i, n in enumerate(names)))
        self.stack.setCurrentIndex(self.step)
        self.back_btn.setEnabled(self.step not in (0, 4, 5))
        self.next_btn.setEnabled(True)
        self.next_btn.setText(T("btn_finish") if self.step == 5 else T("btn_next"))
        if self.step == 0:
            self.say_text(T("say_welcome"))
        elif self.step == 1:
            self.say_text(T("say_agree"))
            self.next_btn.setEnabled(self.agree_box.isChecked())
        elif self.step == 2:
            self.say_text(T("say_mode"))
        elif self.step == 3:
            self.say_text(T("say_path"))
            if self.mode == "auto":
                found = detect_installations(self.payload_kind())
                if found:
                    self.path_edit.setText(str(found[0]))
                    self.path_hint.setText(T("say_path_found"))
                else:
                    self.path_hint.setText(T("say_path_notfound"))
            else:
                self.path_hint.setText(T("say_path_manual"))
        elif self.step == 4:
            pass

    def go(self, delta):
        if self.step == 4:
            return
        if self.step == 3 and delta > 0:
            self.path = self.path_edit.text().strip()
        if self.step == 5 and delta > 0:
            self.close(); return
        self.step = max(0, min(5, self.step + delta))
        self.render()
        if self.step == 4:
            self.start_install()

    def start_install(self):
        target = Path(self.path)
        payload = self.payload_dir()
        found_exe = next((target / n for n in EXE_CANDIDATES if (target / n).exists()), None)
        if found_exe is None:
            msg = T("dlg_new_install_msg", path=str(target))
            ans = QMessageBox.question(self, T("dlg_new_install_title"), msg,
                QMessageBox.Yes | QMessageBox.No)
            if ans != QMessageBox.Yes:
                self.step = 3; self.render(); return
        self.say_text(T("say_installing"))
        self.plog.clear()
        self.worker = Worker(target, payload, self.manifest, restore=False)
        self.worker.progress.connect(lambda p, t: (self.pbar.setValue(p), self.plabel.setText(t)))
        self.worker.log.connect(lambda t: self.plog.appendPlainText("> " + t))
        self.worker.done.connect(self.on_done)
        self.worker.start()

    def on_done(self, ok, msg):
        if ok:
            self.pbar.setValue(100); self.plabel.setText(T("install_done_label"))
            self.say_text(T("say_done"))
            self.finish_body.setText(T("finish_body", msg=msg, path=self.path))
            self.step = 5; self.stack.setCurrentIndex(5); self.render()
        else:
            self.say_text(T("say_failed"))
            QMessageBox.critical(self, T("dlg_failed_title"), msg)
            self.step = 3; self.render()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(T("app_name"))
    global _WIN
    _WIN = Installer()
    _WIN.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
