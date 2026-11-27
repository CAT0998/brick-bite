# Brick Bite v1.3.1

> 本次只有**安装器与文档**的更新，补丁与程序本体与 v1.3.0 完全一致
> （`brick_bite_2.5.2.patch`、`brick_bite_bambu_02.09.02.62.patch` 未改动）。

## 修复

- **Bambu Studio 版安装器现在会自动装好网络插件。**
  Brick Bite 的 Bambu Studio 构建是 internal testing 版，数据目录落在
  `%APPDATA%\BambuStudioInternal`（官方是 `%APPDATA%\BambuStudio`），
  因此官方安装的网络插件对它不可见，程序会一直提示「请在登陆前安装网络插件」，
  而应用内下载在这类构建里又是坏的。
  现在安装器在复制完文件后会自动：读取 `bambu-studio.exe` 版本 → 查询 Bambu 资源接口
  → 下载版本匹配的插件（当前 02.09.02.50）→ 解包到 `%APPDATA%\BambuStudioInternal\plugins`；
  离线时退化为复制官方安装的 `plugins` 目录。完成页会显示「网络插件已就绪」。

## 改进

- **安装器自动检测拓竹（Bambu Studio）安装目录**，不再只认 OrcaSlicer 的常见路径。
- **安装过程不再假死**：进度与日志按百分比节流，几千个「跳过（相同）」不再挤爆消息队列
  （旧版在文件很多时窗口会显示「未响应」）。
- 网络插件的安装放在工作线程里执行，界面保持可响应。

## 文档

- 新增 [`docs/KNOWN-ISSUES.md`](docs/KNOWN-ISSUES.md)：网络插件问题的完整成因（含代码位置）、
  手动修复步骤、OrcaSlicer 为什么没有这个问题、防火墙与安装路径注意事项。

## 安装包

| 包 | 说明 |
|---|---|
| `BrickBite-Bambu-Installer-02.09.02.62.zip` | Bambu Studio 02.09.02.62 + 砖砌咬合（含网络插件自动安装） |
| `BrickBite-Installer-2.5.2.zip` | OrcaSlicer v2.5.2 + 砖砌咬合（安装器同步更新） |

## 校验

安装完成后打开程序：**工艺 → 强度 → 墙 → 砖砌咬合 / Brick bite**，
可选 无 / 半宽交替 / 宽窄交替（Off / Half / Wide）。切片后内墙会按层左右交替偏移。
