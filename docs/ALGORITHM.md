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

当前补丁（`brick_bite_2.5.2.patch` / `brick_bite_bambu_02.09.02.62.patch`）只改 5 个文件；
更早的 `brick_bite.patch`（基于 staggered 分支）还要清理 PR 分支残留的 `staggered_perimeters`，
所以多改一个 `ConfigManipulation.cpp`，共 6 个。

| 文件 | 改动 |
|---|---|
| `src/libslic3r/PrintConfig.hpp` | 新增枚举 `BrickWallMode { none, half, wide }` 与静态映射声明 |
| `src/libslic3r/PrintConfig.cpp` | 新增 `brick_wall_mode` 配置项（三档、中文标签、提示）与枚举映射 |
| `src/libslic3r/Preset.cpp` | 把 `brick_wall_mode` 加入打印参数列表 |
| `src/slic3r/GUI/Tab.cpp` | 在 强度 → 墙 分组里加入该选项 |
| `src/slic3r/GUI/ConfigManipulation.cpp` | 清理旧（PR 分支）`staggered_perimeters` 引用（仅 `brick_bite.patch`） |
| `src/libslic3r/PerimeterGenerator.cpp` | 核心：`apply_brick_outer_width()`，在两个 `process_*` 入口调用 |

核心函数（v1.3.0 起的版本，带护栏）：

```cpp
// 隔层修改首圈（外墙）线宽；外表面保持齐平，内墙整组平移
static void apply_brick_outer_width(PerimeterGenerator &pg)
{
    if (pg.config->brick_wall_mode.value == BrickWallMode::bwmNone)
        return;
    // 螺旋花瓶是一整圈连续外墙，逐层改宽度会把它打断
    if (pg.print_config->spiral_mode.value)      // ← 仅 OrcaSlicer 版有这一条
        return;

    const bool  odd    = (pg.layer_id % 2) == 1;
    const float factor = (pg.config->brick_wall_mode.value == BrickWallMode::bwmHalf)
                             ? (odd ? 0.5f : 1.0f)
                             : (odd ? 0.5f : 1.5f);

    float       w = pg.ext_perimeter_flow.width() * factor;
    const float h = pg.ext_perimeter_flow.height();
    // 护栏：太窄会算出负流量，太宽超过喷嘴的挤出能力
    w = std::max(w, h * 1.25f);
    float max_nozzle = 0.f;
    for (double d : pg.print_config->nozzle_diameter.values)
        max_nozzle = std::max(max_nozzle, float(d));
    if (max_nozzle > 0.f)
        w = std::min(w, max_nozzle * 2.4f);
    pg.ext_perimeter_flow = pg.ext_perimeter_flow.with_width(w);
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

### 失败保护

逐层改首圈线宽在极端参数下会把线宽推出挤出能力的边界，所以写回 flow 之前先做两道夹紧、一道跳过：

| 护栏 | 条件 | 原因 |
|---|---|---|
| 下限夹紧 | `w₀ ≥ 1.25 × 层高` | 线宽小于层高的 1.25 倍时熔道截面比过小，`mm3_per_mm` 有算出**负流量**的风险（half 模式折半后的 `0.5w` 最容易踩到，喷嘴越细越明显） |
| 上限夹紧 | `w₀ ≤ 2.4 × 喷嘴直径` | 线宽超过喷嘴直径的 2.4 倍后，多出来的材料只是被往两侧挤，挤出量线性上升而熔道不再变宽（wide 模式的 `1.5w` 最容易踩到） |
| 花瓶跳过 | `spiral_mode` 为真 → 直接 return | 螺旋花瓶的外墙是一整圈连续上升的单线，逐层改宽度会在层间留下宽度跳变、把螺旋打断；此时保持原线宽，功能整体不生效 |

也就是实际写进 `ext_perimeter_flow` 的线宽为：

```
w₀' = min( max( w₀ · f , 1.25 · h ) , 2.4 · d_n )

f   ：该层的交替系数（0.5 / 1.0 / 1.5）
h   ：层高（ext_perimeter_flow.height()）
d_n ：配置里的最大喷嘴直径（nozzle_diameter 取最大值；为 0 时不做上限夹紧）
```

夹紧只改这一个值，`ring1` 及其后各圈的位置仍由 `Δw₀/2` 推出，所以**错位关系本身不会被破坏**：
`w₀` 被拉回区间后，两层之差同样按夹紧后的实际宽度计算，只是极端参数下错位量会等比变小
（例如 half 模式在窄喷嘴上会小于名义的 `0.5w`），不会出现错乱或重叠加料。

两道夹紧在 OrcaSlicer 与 Bambu Studio 两个补丁里都有；花瓶模式判断只在 OrcaSlicer 版
（`brick_bite_2.5.2.patch`）里。

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
3. 相邻层内墙应整体相差 0.5w（half）或 1.0w（wide）（线宽被夹紧时，按夹紧后的实际线宽换算）；
4. 外墙外表面在各层应保持同一条线（不凸出/不凹陷）。
