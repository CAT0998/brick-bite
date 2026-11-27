# Brick Bite 安装器源码

`main.py`（PySide6 界面）、`netplugin.py`（Bambu 网络插件自动安装）、`i18n.py`（简中/繁中/英文）、
`make_payload.py`（从构建目录生成 payload + manifest.json）、两个 `.spec`（PyInstaller 打包配置）。

构建（需要 `C:\Users\<用户>\bin\python.exe` 这种带 PySide6 的解释器，或自行 `pip install pyside6 pyinstaller`）：

```bash
python make_payload.py <构建输出目录> payload <版本标签>
pyinstaller --noconfirm BrickBite-Bambu-Installer.spec
```

产物 `dist/BrickBite-Bambu-Installer.exe` 与 `payload/`、`使用说明.txt` 一起放进一个目录，
其内容就是发布用 zip 的结构。使用说明见 [../INSTALLER.md](../INSTALLER.md)，
网络插件问题的成因见 [../docs/KNOWN-ISSUES.md](../docs/KNOWN-ISSUES.md)。
