## Brick Bite 现已支持 Bambu Studio 02.08.02.61

把 OrcaSlicer 上的砖砌咬合（Brick Bite）移植到了 **Bambu Studio 02.08.02.61**，并生成了独立的安装器。

### 原理
隔层只改**外墙（first ring）线宽**：

| 模式 | 效果 |
|---|---|
| `Half (0.5w <-> w)` | 奇数层外墙 0.5×，偶数层 1× |
| `Wide (0.5w <-> 1.5w)` | 奇数层 0.5×，偶数层 1.5× |

内圈位置随外墙宽度自动偏移 `Δw/2`，墙缝落在两层中间，形成砖砌咬合。

### 安装
1. 下载 Release 里的 `BrickBite-Bambu-Installer-02.08.02.61.zip`；
2. 解压后双击安装器，选择你的 Bambu Studio 目录；
3. 原文件自动备份为 `*.brickbite.bak`，支持回滚。

设置位置：**工艺 → 强度 → 墙 → Brick wall mode**

### 已验证
- 依赖全部编译通过（OCCT / OpenVDB / wxWidgets / Boost / OpenCV 等）
- 主程序可正常启动
- `BambuStudio.dll` 含 `Brick bite: alternating first-ring half width` / `brick_wall_mode` / `Half (0.5w <-> w)` / `Wide (0.5w <-> 1.5w)`
- 安装器 payload 逻辑测试：替换 / 哈希校验 / 备份 / 无关文件不动 / 回滚

### 下载
https://github.com/CAT0998/brick-bite/releases/tag/v1.2.0

### 说明
- 仅修改切片外墙宽度，不动内墙、填充与支撑；
- 已处理螺旋花瓶模式（自动跳过）与线宽上下限保护；
- 上游 AGPL-3.0，修改部分同样以 AGPL-3.0 发布；
- 想法：@CAT0998；实现：AI（deepseek-flash / DeepSeek-V4.1-Flash）。
