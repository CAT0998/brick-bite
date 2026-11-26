# Brick Bite for Bambu Studio 02.08.02.61

把 OrcaSlicer 上的砖砌咬合（Brick Bite）移植到 **Bambu Studio 02.08.02.61**。

## 这是什么

隔层只改**外墙（first ring）线宽**，让相邻层的墙缝错开：

| 模式 | 效果 |
|---|---|
| `Half (0.5w <-> w)` | 奇数层外墙宽度降到 0.5×，偶数层恢复 1× |
| `Wide (0.5w <-> 1.5w)` | 奇数层 0.5×，偶数层 1.5× |

内圈位置随外墙宽度变化自动偏移 `Δw/2`，所以墙缝落在两层中间，形成砖砌咬合，层间结合强度更高。

设置位置：**工艺 → 强度 → 墙 → Brick wall mode**

## 安装

下载 `BrickBite-Bambu-Installer-02.08.02.61.zip`，解压后双击安装器，选择你的 Bambu Studio 目录即可。安装器会自动备份原文件（`*.brickbite.bak`），支持回滚。

## 已验证

- ✅ 依赖全部编译通过（OCCT / OpenVDB / wxWidgets / Boost / OpenCV 等）
- ✅ 主程序 `bambu-studio.exe` 可正常启动
- ✅ `BambuStudio.dll` 内含 `Brick bite: alternating first-ring half width`、`brick_wall_mode`、`Half (0.5w <-> w)`、`Wide (0.5w <-> 1.5w)`
- ✅ 安装器 payload 逻辑测试：替换、哈希校验、备份、无关文件不动、回滚

## 说明

- 仅改外墙线宽，不动内墙、填充、支撑；
- 已处理螺旋花瓶模式（自动跳过）与线宽上下限保护；
- Bambu Studio 上游为 AGPL-3.0，修改部分同样以 AGPL-3.0 发布；
- 作者：想法 @CAT0998，实现由 AI 完成（deepseek-flash / DeepSeek-V4.1-Flash）。

## 风险

- 外墙变窄时，极端参数下可能出现墙面不均；建议先用小模型测试；
- 本补丁只改切片逻辑，不影响打印机固件。
