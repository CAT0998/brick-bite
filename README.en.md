# Brick Bite

**Alternating first-ring half-width offset · brick-style Z interlacing for FDM walls**
A wall-interlacing algorithm for FDM slicers, shipped as a patch for OrcaSlicer.

> **Attribution — please read first**
>
> **Everything in this repository (code, analysis, documentation, build scripts, this file) was produced by an AI agent** —
> DeepSeek Harness running the `deepseek-flash` model (DeepSeek-V4.1-Flash, build 1017).
> The human project owner contributed **only the idea and the direction**: “shift the whole inner-wall block by
> changing the first ring's line width instead of moving paths”.
> The AI did the research, the math, the implementation, the compilation, the debugging and the writing.
>
> Free and open source. Commercial use is allowed. **Nobody may patent this algorithm to extract fees or build a monopoly.**

---

## 1. The problem

FDM parts are weakest along Z. Walls are stacked at the same XY position layer after layer, so the seams line up
and parts split along them.

The known mitigation is **Brick Layers / Staggered Perimeters**: shift walls sideways on alternating layers so they
interlock like brickwork.

Existing implementations mostly:

- offset the whole wall geometry (Clipper offset) — distorts contours and creates gaps in circular / holed parts;
- post-process G-code — no notion of "which loop, which layer", seams and mismatches;
- add an extra wall every other layer — more material and time, and not a true stagger.

**Brick Bite takes a different route: one geometric relation solves everything.**

---

## 2. How it works

Let `B` be the model boundary, `w₀` the outer-wall line width and `w₁` the inner-wall line width.

When a slicer generates walls by offsetting inward, the ring positions are:

```
ring 0 (outer):  centre = B − w₀/2                  ← outer face always on B
ring 1 (inner):  centre = B − (2·w₀ + w₁)/2
ring 2..n:       every further ring by perimeter_spacing
```

Hence:

```
whole inner-wall block = B − (2·w₀ + w₁)/2
```

**Changing only the first ring's line width `w₀` translates every inner ring:**

```
Δinner = Δw₀ / 2
```

And since the outer ring's centreline is always `B − w₀/2`, **the outer surface stays flush** — it never bulges or
sinks, regardless of `w₀`.

The spacing between neighbouring rings equals the sum of their half widths:

```
spacing(0→1) = (w₀ + w₁)/2 = w₀/2 + w₁/2
```

so there is **no overlap and no gap**.

### Modes

| Mode | outer wall width (odd ↔ even layers) | inner-wall shift between layers |
|---|---|---|
| Off | — | 0 |
| Half | 0.5w ↔ w | 0.5w (0.225 mm at 0.45 width) |
| Wide | 0.5w ↔ 1.5w | 1.0w (0.45 mm at 0.45 width) |

---

## 3. How it differs from existing work

| Approach | Changes geometry | Adds paths | Circular / holed parts | Outer surface |
|---|---|---|---|---|
| Bricklayers / staggered perimeters | yes (offset) | no | gaps likely | needs compensation |
| Alternate extra wall | no | yes (extra loop) | fine | unchanged |
| G-code post-processing | yes (coordinates) | no | seams hard to fix | error-prone |
| **Brick Bite** | **no** | **no** | **fine** | **flush by construction** |

No public implementation of “vary the first ring's width to translate the whole inner block” was found during
research, so it is published here as an independent idea and as a **defensive publication**.

---

## 4. Quick start

### 4.1 Apply the patch

The patch is based on the `staggered-perimeters-rebased` branch of OrcaSlicer
(the branch used by PR #8181):

```bash
git clone https://github.com/vipulrajan/OrcaSlicer -b staggered-perimeters-rebased
cd OrcaSlicer
git apply /path/to/brick_bite.patch
```

### 4.2 Build (Windows)

See `docs/BUILD.md`: VS 2022 Build Tools + CMake + Strawberry Perl.
If GitHub is blocked, rewrite dependency URLs with `https://ghproxy.net/https://github.com/`.

### 4.3 Use

After building, in **Process → Strength → Walls**:

```
Brick bite: alternating first-ring half width
  ├─ Off
  ├─ Half   (0.5w ↔ w)
  └─ Wide   (0.5w ↔ 1.5w)
```

Try **Half** first, then **Wide**.

---

## 5. Known limitations

1. **Surface banding** — the outer wall width alternates per layer, so the outer surface shows a wide/narrow texture.
   This is inherent to the method;
2. **Both outer loops change** — outer contour and hole walls share the same flow, so both get wider/narrower at the
   same time (directions are consistent, so no distortion);
3. **Extrusion stability** — 0.5w (0.225 mm at 0.45) is narrow and 1.5w is wide; flow / pressure advance may need tuning;
4. **Arachne variable width** — thin walls and overhangs already vary their width; test before relying on it;
5. Only PLA/PETG with common settings were tested.

---

## 6. Disclaimer (summary)

Full text: [DISCLAIMER.md](DISCLAIMER.md).

- Provided **as is**, without any warranty;
- Printing failures, machine damage or material waste are **the user's responsibility**;
- **Not affiliated with the OrcaSlicer project**;
- This project **grants no patent rights** and does not endorse any third-party patent claim.

---

## 7. License and anti-patent statement

- Code is released under **AGPL-3.0** (same as OrcaSlicer);
- **Commercial use is allowed** (including integration into commercial slicers and print services);
- **Explicitly forbidden**: any organisation or individual patenting this algorithm (its mathematical relation,
  mode split or implementation) to charge fees, litigate or create a monopoly;
- The public history of this repository is intended as **prior art** to prevent such patents from being granted.

---

> Note: the detailed docs under `docs/` are currently in Chinese; this README summarizes them in English.

## 8. Development story

See [docs/STORY.md](docs/STORY.md). Short version: G-code post-processing failed (no XY movement), in-slicer polygon
offsets produced gaps on rings, then the human owner proposed “just change the first ring's width” — the AI derived
the relation, implemented it, built a custom OrcaSlicer and verified the result.

## 9. Authors and credits

- **Idea, direction, testing**: the project owner — **@CAT0998** (https://github.com/CAT0998)
- **Research, implementation, build, documentation, this README**: AI — DeepSeek Harness / `deepseek-flash` (DeepSeek-V4.1-Flash, build 1017)
- Thanks to the OrcaSlicer project and the author of PR #8181 for the foundation.

---

## 10. A small note about the tool

This project is also a data point about how far an AI coding agent can go on real engineering work:
reading a large C++ codebase, deriving the geometry, writing the patch, setting up a full Windows build
(VS 2022, CMake, Perl, dependency proxies), fixing linker errors and validating the result.

If you find this useful, consider giving **DeepSeek** and **DeepSeek Harness** a try — the whole implementation
here was produced with it.
