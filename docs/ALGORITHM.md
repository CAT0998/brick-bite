# 算法详解：Brick Bite（砖砌咬合）

本文描述算法的完整流程、数学依据与代码落点，便于他人复现或移植到其它切片器。

---

## 1. 传统切片的墙生成流程

以 OrcaSlicer 为例（`LayerRegion::make_perimeters` → `PerimeterGenerator::process_classic/process_arachne`）：

```
模型网格 TriangleMesh
   │  切片
   ▼
每层截面 ExPolygons（外轮廓 + 孔洞，已合并/去重）
   │  表面分类（顶/底/中间/桥接）
   ▼
生成墙 PerimeterGenerator
   │  ① 由外向内逐圈 offset
   │     第 0 圈：offset(-w₀/2)   → 外墙，外表面贴模型
   │     第 1 圈：offset(-(w₀+w₁)/2)
   │     第 n 圈：再 offset(-perimeter_spacing)
   ▼
ExtrusionLoop / ExtrusionPath（坐标 + 线宽）
   │
   ▼
G-code（G1 X Y E）
```

**关键点：墙的“位置”由上一圈的间距决定，而间距由线宽决定。**

---

## 2. Brick Bite 的数学推导

记号：

- `B`：模型边界（截面的外轮廓或孔洞边界）
- `w₀`：首圈（外墙）线宽
- `w₁`：内墙线宽
- `s`：内墙间距 `perimeter_spacing`（由 `w₁` 决定，本算法不改）

各圈中心线位置：

```
ring0 = B − w₀/2
ring1 = ring0 − (w₀ + w₁)/2 = B − (2w₀ + w₁)/2
ring2 = ring1 − s
ring3 = ring2 − s
...
```

因此：

1. **ring0 的外表面** = `ring0 + w₀/2` = `B` → 无论 `w₀` 怎么变，外表面都齐平；
2. **ring1 及其后所有圈** 都随 `w₀` 平移 `Δw₀/2`；
3. **相邻圈间距** = 两者半宽之和，线与线相切，**无重叠、无空隙**。

### 两种交替模式

| 模式 | 奇数层 w₀ | 偶数层 w₀ | ring1 位置差 |
|---|---|---|---|
| half | 0.5w | w | 0.5w |
| wide | 0.5w | 1.5w | 1.0w |

以 w=0.45 为例：half 模式错位 0.225 mm，wide 模式错位 0.45 mm。

---

## 3. 代码改动

补丁只改 6 个文件（见 `brick_bite.patch`）：

| 文件 | 改动 |
|---|---|
| `src/libslic3r/PrintConfig.hpp` | 新增枚举 `BrickWallMode { none, half, wide }` 与静态映射声明 |
| `src/libslic3r/PrintConfig.cpp` | 新增 `brick_wall_mode` 配置项（三档、中文标签、提示）与枚举映射 |
| `src/libslic3r/Preset.cpp` | 把 `brick_wall_mode` 加入打印参数列表 |
| `src/slic3r/GUI/Tab.cpp` | 在 强度 → 墙 分组里加入该选项 |
| `src/slic3r/GUI/ConfigManipulation.cpp` | 清理旧（PR 分支）`staggered_perimeters` 引用 |
| `src/libslic3r/PerimeterGenerator.cpp` | 核心：`apply_brick_outer_width()`，在两个 `process_*` 入口调用 |

核心函数：

```cpp
// 隔层修改首圈（外墙）线宽；外表面保持齐平，内墙整组平移
static void apply_brick_outer_width(PerimeterGenerator &pg)
{
    if (pg.config->brick_wall_mode.value == BrickWallMode::bwmNone)
        return;
    const bool odd = (pg.layer_id % 2) == 1;
    float factor;
    if (pg.config->brick_wall_mode.value == BrickWallMode::bwmHalf)
        factor = odd ? 0.5f : 1.0f;
    else
        factor = odd ? 0.5f : 1.5f;
    pg.ext_perimeter_flow =
        pg.ext_perimeter_flow.with_width(pg.ext_perimeter_flow.width() * factor);
}
```

调用位置：

```cpp
void PerimeterGenerator::process_classic()
{
    apply_brick_outer_width(*this);   // ← 必须在所有 spacing 计算之前
    ...
}

void PerimeterGenerator::process_arachne()
{
    apply_brick_outer_width(*this);
    ...
}
```

### 为什么改 flow 就够了

`PerimeterGenerator` 里所有相关量都在 `process_*` 内部由 `ext_perimeter_flow` 推导：

```
ext_perimeter_width    = ext_perimeter_flow.scaled_width()
ext_perimeter_spacing  = ext_perimeter_flow.scaled_spacing()
ext_perimeter_spacing2 = 0.5 * (外墙宽 + 内墙宽)      // ring0→ring1 间距
fill_clip              = 由 ext_perimeter_spacing 推导
每条路径的 width/mm3   = 取自对应 flow
```

在入口处改掉 flow，后续全部自动一致，无需改动 offset 逻辑本身。

---

## 4. 移植到其它切片器

任何切片器只要满足以下条件，都可以用同样的思路：

1. 墙是“从边界向内按间距逐圈 offset”生成的；
2. 首圈的 offset 距离等于其半宽（保证外表面贴模型）；
3. 后续间距由相邻圈线宽推导。

改动点只有一处：**按层覆写首圈线宽**。

---

## 5. 验证方法

1. 用 45° 斜面 + 圆孔模型切片；
2. 导出 G-code，统计每层内墙的坐标（X 或 Y 的极值）；
3. 相邻层内墙应整体相差 0.5w（half）或 1.0w（wide）；
4. 外墙外表面在各层应保持同一条线（不凸出/不凹陷）。
