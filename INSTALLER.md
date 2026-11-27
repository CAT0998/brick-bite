# 安装器（Installer）说明

本项目提供 Windows 安装器，当前发布的是 **OrcaSlicer v2.5.2** 与 **Bambu Studio 02.09.02.62** 两个版本：

| 版本 | 说明 |
|---|---|
| **BrickBite-Installer-2.5.2** | 基于 OrcaSlicer **v2.5.2** 官方发布源码 + `brick_bite_2.5.2.patch` 构建（当前） |
| **BrickBite-Bambu-Installer-02.09.02.62** | 基于 Bambu Studio **02.09.02.62**（官方名 2.9.2 Public Release）+ `brick_bite_bambu_02.09.02.62.patch` 构建（当前） |
| **BrickBite-Installer-2.4.2** | 基于 OrcaSlicer **v2.4.2** 官方发布源码 + 本仓库补丁构建 |
| **BrickBite-Installer-2.3.2** | 基于 `staggered-perimeters-rebased` 分支构建（2.3.2-dev） |

## 它做什么

OrcaSlicer 与 Bambu Studio 都没有插件接口，砖砌咬合是编译进程序的，所以安装器不是“挂载插件”，而是：

1. 找到你已安装的 OrcaSlicer / Bambu Studio（自动检测或手动选择）；
2. 按 **SHA256 哈希**逐个比对文件：
   - 已经相同 → 跳过（不动）；
   - 缺失或不同 → 备份为 `*.brickbite.bak` 后替换；
3. 需要时创建桌面快捷方式；
4. 所有被替换的文件都可以恢复。

因为只替换有差异的文件，`resources/`（约 172 MB 的预设与图标）通常完全跳过。

## 使用

1. 解压安装器压缩包，得到：
   ```
   BrickBite Installer.exe
   payload\            （程序文件 + manifest.json）
   ```
2. 双击 `BrickBite Installer.exe`；
3. 阅读并同意许可与免责声明；
4. 选择「自动检测」或「手动选择」目标目录（OrcaSlicer 安装器选 OrcaSlicer 目录，Bambu 安装器选 Bambu Studio 目录）；
5. 点“下一步”开始，等待进度条完成；
6. 打开 OrcaSlicer / Bambu Studio → 工艺 → 强度 → 墙 → **砖砌咬合：首圈半宽交替 (Brick bite)**。

## 版本匹配（重要）

安装器只替换文件，**不改变程序版本**。请务必注意：

- 2.5.2 安装器用于 **OrcaSlicer v2.5.2**；
- `BrickBite-Bambu-Installer-02.09.02.62` 用于 **Bambu Studio 2.9.2（02.09.02.62）**；
- 2.4.2 安装器用于 **OrcaSlicer 2.4.2**；
- 2.3.2 安装器用于 2.3.2-dev 构建；
- 版本不一致时可能出现崩溃，安装器会尽量提示，但不保证拦截。

如果目标目录里没有对应的可执行文件（OrcaSlicer 是 `orca-slicer.exe`，Bambu Studio 是 `bambu-studio.exe`），
安装器会询问是否作为“全新安装目录”，此时会写入完整程序。

## 网络插件（Bambu Studio 版）

Bambu Studio 的 Brick Bite 构建是 internal testing 版，数据目录是
`%APPDATA%\BambuStudioInternal`（官方版是 `%APPDATA%\BambuStudio`）。
官方安装的网络插件在官方目录里，这个构建看不到，程序会一直提示「请在登陆前安装网络插件」，
而应用内下载在这类构建里是坏的。

所以 **v1.3.1 起的 Bambu 安装器**在复制完文件后会：

1. 读取目标目录里 `bambu-studio.exe` 的版本（例如 02.09.02.62）；
2. 向 `api.bambulab.com` 查询该版本对应的网络插件（当前是 02.09.02.50）；
3. 下载约 47 MB 的插件包，解包到 `%APPDATA%\BambuStudioInternal\plugins`；
4. 离线或接口不可用时，退化为把官方安装的 `%APPDATA%\BambuStudio\plugins` 复制过去。

完成页会显示「网络插件已就绪」。首次启动时 Windows 防火墙会询问，选「允许访问」即可。

详细成因与手动修复步骤见 [docs/KNOWN-ISSUES.md](docs/KNOWN-ISSUES.md)。

## 恢复原版

被替换的文件都有 `*.brickbite.bak` 备份。手动恢复即可：

```
把 OrcaSlicer.dll.brickbite.bak 改回 OrcaSlicer.dll
把 BambuStudio.dll.brickbite.bak 改回 BambuStudio.dll
```

## 安全与许可

- 安装器不收集、不上传任何数据；Bambu Studio 版在安装完成后会向 Bambu 官方资源接口发起一次查询并下载网络插件（见上一节），除此之外不访问网络；
- 许可：AGPL-3.0（与 OrcaSlicer 一致）；
- 免责声明见 [DISCLAIMER.md](DISCLAIMER.md)；
- 想法 / 方向 / 测试：**@CAT0998**；实现 / 分析 / 编译 / 文档：**AI — DeepSeek Harness / deepseek-flash**。
