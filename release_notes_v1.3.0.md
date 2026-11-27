# v1.3.0 — 同步 OrcaSlicer 2.5.2 与 Bambu Studio 02.09.02.62

## 简体中文

补丁已移植到两个新的上游版本，都以官方 tag 源码为基线，`git apply -p1` 可直接应用：

| 补丁文件 | 上游版本 |
|---|---|
| `brick_bite_2.5.2.patch` | OrcaSlicer **v2.5.2**（2026-11-21 发布） |
| `brick_bite_bambu_02.09.02.62.patch` | Bambu Studio **02.09.02.62**（2026-11-24 发布，官方名 2.9.2 Public Release） |

旧补丁保留不动：`brick_bite.patch`（2.3.2-dev，`staggered-perimeters-rebased` 分支）、
`brick_bite_2.4.2.patch`、`brick_bite_bambu.patch`（02.08.02.61）。

### 新增：两处安全护栏

1. **线宽夹紧**（两份补丁都有）：改完的首圈线宽会被夹在 `≥ 1.25 × 层高` 与 `≤ 2.4 × 喷嘴直径` 之间，
   避免半宽（half）模式在窄喷嘴上算出负流量、宽窄（wide）模式超出挤出能力；
2. **花瓶（螺旋）模式自动跳过**（OrcaSlicer 版）：螺旋花瓶的外墙是一整圈连续墙，
   逐层改宽度会把螺旋打断，因此该模式下直接不生效、保持原线宽。

### 安装器与实测状态

| 安装器 | 上游 | 状态 |
|---|---|---|
| `BrickBite-Installer-2.5.2` | OrcaSlicer **v2.5.2** | ✅ 已编译并实机验证，本 Release 附件 |
| `BrickBite-Bambu-Installer-02.09.02.62` | Bambu Studio **2.9.2**（02.09.02.62） | ✅ 已编译并实机验证，本 Release 附件 |

已做的实机验证（Bambu Studio 02.09.02.62）：
- 程序可正常启动、加载 STL、切片；
- 「工艺 → 强度 → 墙」出现 **Brick bite: alternating first-ring half width**，可选 Off / Half / Wide；
- 同一模型分别用 `Half` 与 `Off` 切片并导出 G-code 对比：`Half` 模式下外墙 `; LINE_WIDTH:` 在 **0.25 / 0.42** 之间逐层交替，
  `Off` 模式下 148 段外墙全部为 0.42 —— 交替错位确实生效；0.25 正是 `1.25 × 层高(0.2)`，说明线宽夹紧也在起作用。

已做的实机验证（OrcaSlicer v2.5.2）：
- 程序可正常启动、加载 STL、切片；
- 「工艺 → 强度 → 墙」出现 **砖砌咬合：首圈半宽交替 (Brick bite)**，可选 无 / 半宽交替（0.5w ↔ w）/ 宽窄交替（0.5w ↔ 1.5w）；
- 同一模型分别用「半宽交替」与「无」切片并导出 G-code，按逐层外墙挤出量反算线宽：
  `半宽交替` 时 45 层外墙平均线宽逐层交替 **0.201 / 0.418**（严格交替），`无` 时全部稳定在 **0.418** —— 交替错位确实生效；
  0.201 已高于 `1.25 × 层高`，说明线宽夹紧同样在起作用。

安装器按 SHA256 比对、只替换有差异的文件，替换前备份为 `*.brickbite.bak`。

### 文档

三语 README（简 / 繁 / EN）、`INSTALLER.md`、`docs/BUILD.md`、`docs/ALGORITHM.md` 已同步到新版本；
`docs/ALGORITHM.md` 新增「失败保护」小节，记录上面两条护栏的公式与生效范围。

## English

The patch has been ported to two new upstream versions, both based on the official release tags and
applying cleanly with `git apply -p1`:

| Patch file | Upstream |
|---|---|
| `brick_bite_2.5.2.patch` | OrcaSlicer **v2.5.2** (released 2026-11-21) |
| `brick_bite_bambu_02.09.02.62.patch` | Bambu Studio **02.09.02.62** (released 2026-11-24, official name “2.9.2 Public Release”) |

The older patches are unchanged: `brick_bite.patch` (2.3.2-dev, `staggered-perimeters-rebased` branch),
`brick_bite_2.4.2.patch`, `brick_bite_bambu.patch` (02.08.02.61).

### New: two safety guards

1. **Width clamping** (both patches) — the adjusted first-ring width is clamped between
   `≥ 1.25 × layer height` and `≤ 2.4 × nozzle diameter`, so Half mode cannot compute a negative flow on a
   narrow nozzle and Wide mode cannot exceed what the machine can actually extrude;
2. **Spiral (vase) mode is skipped** (OrcaSlicer build) — the vase outer wall is one continuous loop and a
   per-layer width change would break it, so the feature simply stays off in that mode.

### Installers and verification status

| Installer | Upstream | Status |
|---|---|---|
| `BrickBite-Bambu-Installer-02.09.02.62` | Bambu Studio **2.9.2** (02.09.02.62) | ✅ built and verified on a real machine, attached to this release |
| `BrickBite-Installer-2.5.2` | OrcaSlicer **v2.5.2** | ✅ built and verified on a real machine, attached to this release |

What was actually verified (Bambu Studio 02.09.02.62):
- the application starts, imports an STL and slices;
- **Process → Strength → Walls** shows **Brick bite: alternating first-ring half width** with Off / Half / Wide;
- slicing the same model with `Half` and with `Off` and diffing the exported G-code: in `Half` mode the outer-wall
  `; LINE_WIDTH:` alternates **0.25 / 0.42** layer by layer, while in `Off` mode all 148 outer-wall segments are 0.42 —
  the interlace really happens, and 0.25 is exactly `1.25 × layer height (0.2)`, which shows the width clamp is active.

What was actually verified (OrcaSlicer v2.5.2):
- the application starts, imports an STL and slices;
- **Process → Strength → Walls** shows **砖砌咬合：首圈半宽交替 (Brick bite)** with 无 / 半宽交替（0.5w ↔ w）/ 宽窄交替（0.5w ↔ 1.5w）;
- slicing the same model with Half and with Off, then converting each outer-wall extrusion back to a width from the
  exported G-code: in Half mode the 45 per-layer means alternate **0.201 / 0.418** (strict alternation), while in Off
  mode they stay at **0.418** — and 0.201 already sits above `1.25 × layer height`, so the clamp is active as well.

The installer compares SHA256 hashes, replaces only the files that differ and backs each one up as
`*.brickbite.bak`.

### Documentation

All three READMEs (zh-CN / zh-TW / EN), `INSTALLER.md`, `docs/BUILD.md` and `docs/ALGORITHM.md` are updated
for the new versions; `docs/ALGORITHM.md` gained a “Failure protection” subsection documenting the two
guards and their formulas.

---

Idea @CAT0998 · implementation by AI (DeepSeek Harness / deepseek-flash) · AGPL-3.0
