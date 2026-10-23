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

```bash
git clone https://github.com/vipulrajan/OrcaSlicer -b staggered-perimeters-rebased
cd OrcaSlicer
git apply /path/to/brick_bite.patch
```

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
