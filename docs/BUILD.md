# 编译说明（Windows）

## 1. 环境

| 组件 | 版本/说明 |
|---|---|
| Visual Studio 2022 Build Tools | C++ 工作负载 + Windows 10/11 SDK |
| CMake | ≥ 3.2x |
| Strawberry Perl | 必须是 Strawberry（MSYS/Cygwin 的 perl 会导致 OpenSSL 配置失败） |
| 磁盘 | 依赖 + 构建约 25–40 GB |
| 内存 | ≥ 12 GB |

打开 Windows 长路径支持（管理员）：

```
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

## 2. 获取源码

基线是官方 tag：OrcaSlicer **v2.5.2**、Bambu Studio **v02.09.02.62**（官方名 2.9.2 Public Release）。

```bash
# OrcaSlicer v2.5.2
git clone https://github.com/OrcaSlicer/OrcaSlicer -b v2.5.2 --depth 1
cd OrcaSlicer
git apply -p1 /path/to/brick_bite_2.5.2.patch
```

```bash
# Bambu Studio v02.09.02.62
git clone https://github.com/bambulab/BambuStudio -b v02.09.02.62 --depth 1
cd BambuStudio
git apply -p1 /path/to/brick_bite_bambu_02.09.02.62.patch
```

Bambu Studio 的 Windows 构建脚本是仓库根目录的 `build_win.bat`；OrcaSlicer 用第 4 节的
`build_release_vs2022.bat`。旧补丁（`brick_bite_2.4.2.patch`、`brick_bite_bambu.patch`、
`brick_bite.patch`）保留，仅用于对应旧上游。

### 2.1 国内网络下载源码

`github.com` 不可达、但 `codeload.github.com` 还能连时，不用代理，直接把归档地址换掉即可：

```
原来: https://github.com/<owner>/<repo>/archive/refs/tags/<tag>.zip
换成: https://codeload.github.com/<owner>/<repo>/zip/refs/tags/<tag>
```

例如：

```
https://codeload.github.com/OrcaSlicer/OrcaSlicer/zip/refs/tags/v2.5.2
https://codeload.github.com/bambulab/BambuStudio/zip/refs/tags/v02.09.02.62
```

注意这里**不需要** `.zip` 后缀，codeload 会直接返回 zip 流（`<repo>-<tag>.zip`）；
解压后的目录名与 `git clone` 略有不同（通常是 `<repo>-<tag>`），后续脚本里的路径按实际目录名调整。

## 3. 依赖下载（网络受限时）

若 `github.com` 无法访问，可把所有依赖 URL 前缀替换为代理：

```python
# 在 deps 目录下执行
import os
for root, _, files in os.walk("deps"):
    for f in files:
        if f.endswith((".cmake", ".txt")):
            p = os.path.join(root, f)
            s = open(p, encoding="utf-8", errors="ignore").read()
            if "https://github.com/" in s and "ghproxy.net" not in s:
                open(p, "w", encoding="utf-8").write(
                    s.replace("https://github.com/", "https://ghproxy.net/https://github.com/"))
```

另外：

- `deps/OpenCV/OpenCV.cmake` 里的 `-DWITH_IPP=ON` 建议改为 `OFF`（IPPICV 下载易失败）；
- `deps/wxWidgets/wxWidgets.cmake` 的 `GIT_SHALLOW ON` 后建议加 `UPDATE_DISCONNECTED 1`。

> **和 2.4.2 的差别**：OrcaSlicer 2.5.2 的依赖版本有明显升级（CGAL 5.6.3 → 6.2.1、GMP 6.3.0、
> PNG 1.6.59 等），所以**首次构建依赖的时间会比 2.4.2 长不少**，机型慢的话请预留出额外的时间与磁盘。

## 4. 编译

```bat
set PATH=<strawberry>\perl\bin;<strawberry>\c\bin;<cmake>\bin;%PATH%
build_release_vs2022.bat deps
set WindowsSdkDir=C:\Program Files (x86)\Windows Kits\10\
set WindowsSDKVersion=10.0.22621.0\
build_release_vs2022.bat slicer
```

构建产物：`build\OrcaSlicer\orca-slicer.exe`。

## 5. 常见问题

| 现象 | 处理 |
|---|---|
| OpenSSL 配置报 `perl implementation doesn't produce Windows like paths` | 换 Strawberry Perl，并清掉 `PERL5LIB`/`PERL5OPT` |
| wxWidgets 配置报 `MSB6003 ... WinIOError` | 开启长路径支持 |
| `LNK2001` 大量未解析符号 | 新枚举缺少 `CONFIG_OPTION_ENUM_DECLARE/DEFINE_STATIC_MAPS` |
| 依赖被系统里其它软件的同名包干扰 | 临时改名 `C:\Users\<用户>\lib\cmake` |
| 编译太慢 | 可在 `build_release_vs2022.bat` 里用 `-m:3` 限制并行核数 |
