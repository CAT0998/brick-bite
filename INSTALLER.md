# 安装器（Installer）说明

本项目提供两个 Windows 安装器：

| 版本 | 说明 |
|---|---|
| **BrickBite-Installer-2.3.2** | 基于 `staggered-perimeters-rebased` 分支构建（2.3.2-dev） |
| **BrickBite-Installer-2.4.2** | 基于 OrcaSlicer **v2.4.2** 官方发布源码 + 本仓库补丁构建 |

## 它做什么

OrcaSlicer 没有插件接口，砖砌咬合是编译进程序的，所以安装器不是“挂载插件”，而是：

1. 找到你已安装的 OrcaSlicer（自动检测或手动选择）；
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
4. 选择「自动检测」或「手动选择」OrcaSlicer 目录；
5. 点“下一步”开始，等待进度条完成；
6. 打开 OrcaSlicer → 工艺 → 强度 → 墙 → **砖砌咬合：首圈半宽交替 (Brick bite)**。

## 版本匹配（重要）

安装器只替换文件，**不改变程序版本**。请务必注意：

- 2.4.2 安装器用于 **OrcaSlicer 2.4.2**；
- 2.3.2 安装器用于 2.3.2-dev 构建；
- 版本不一致时可能出现崩溃，安装器会尽量提示，但不保证拦截。

如果目标目录里没有 `orca-slicer.exe`，安装器会询问是否作为“全新安装目录”，此时会写入完整程序。

## 恢复原版

被替换的文件都有 `*.brickbite.bak` 备份。手动恢复即可：

```
把 OrcaSlicer.dll.brickbite.bak 改回 OrcaSlicer.dll
```

## 安全与许可

- 安装器不联网、不收集任何数据；
- 许可：AGPL-3.0（与 OrcaSlicer 一致）；
- 免责声明见 [DISCLAIMER.md](DISCLAIMER.md)；
- 想法 / 方向 / 测试：**@CAT0998**；实现 / 分析 / 编译 / 文档：**AI — DeepSeek Harness / deepseek-flash**。
