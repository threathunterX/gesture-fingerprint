# Experiment data & methodology

**English** · [中文](../README.md)

The evidence behind every rule in [gesture-fingerprint](../../README.en.md).

We bought 8 classes of off-the-shelf cheating hardware, built 2 software script
baselines, had a human and every tool perform identical gestures under a range of
phone states, collected **75,386 labelled gestures**, compared them across
9 dimensions, and froze the result into a runnable rule engine.

## Contents

| Document | Covers |
|---|---|
| [01 · Experiment method](./01-experiment-method.md) | Which devices, which scenarios, how many samples, field spec |
| [02 · The nine dimensions](./02-nine-dimensions.md) | **Core.** What a human and each tool look like on every dimension |
| [03 · Decision rules](./03-decision-rules.md) | From findings to 18 rules, plus the thresholds actually in the code |
| [04 · Validation & limits](./04-validation-and-limits.md) | Blind-test results, error attribution, what this cannot do |

> **About the figures.** The statistical charts were produced during the original
> analysis and are labelled in Chinese. Rather than leave them unexplained, every
> figure in these English pages carries a caption stating exactly what to look at,
> and the numbers behind it are reproduced in English tables. The trajectory
> figures have been **re-rendered in English** from the blind-test data shipped in
> this repo — the script is at
> [`.github/gen_traj_en.py`](../../.github/gen_traj_en.py), so you can reproduce
> or restyle them yourself.

---

## One page

**Stable ordering by how human-like a tool is:**

```
hand-written script  <  mouse clicker  <  capacitive clicker  <  robotic arm  <  human
    least human                                                            most human
```

**Discriminative power of the nine dimensions:**

| Dimension | Power | In one line |
|---|---|---|
| Speed variability (swipe) | very high | Scripts ≈ 0; human ≈ 0.51; robotic arm ≈ 0.65; screen-swiper A highest at ≈ 1.09 |
| Contact area | very high | Software injection / HID / mouse clicker are 0; human largest |
| Pressure | high | Scripts / HID pinned at 1.0; human's distribution is the widest |
| Pressure variability | high | Scripts ≈ 0; human P50 ≈ 0.23 |
| Mean swipe speed | medium-high | Auto-liker fastest, mouse clicker slowest |
| Path redundancy | medium | A human's stroke tail is far longer than the arm's — more genuine detours |
| Mean curvature | medium | Scripts ≈ 0; the robotic arm actually varies *more* than a human |
| Linear acceleration | medium | Whether the phone is genuinely held and moved |
| Gyroscope | medium | Same; surprisingly strong in the "phone upright in a stand" scenario |

**How many dimensions, exactly?**

| | Count | Note |
|---|---|---|
| Dimensions in the analysis | **9** | The table above |
| Features the engine reads | **10** | Those 9 **plus tap spatial distribution** (fixed-point repeat / local offset / full-screen random). It is a batch-level feature and applies to taps only, which is why it is not counted among "the nine" |
| Typically active in production | **7** | Linear acceleration and gyroscope need a phone-state label that production telemetry rarely carries. Having the engine infer phone state itself is [Issue #4](../../../../issues/4) |

One analysis finding **never made it into the code**: dimension 4 established that a
human's swipe speed follows a distinct accelerate–peak–decelerate profile, but the
engine currently uses only the scalar *mean* speed, with no curve-shape matching.
Tracked as [Issue #5](../../../../issues/5).

---

## The single most important conclusion

> The most human-like tool — the robotic arm — can beat **any one dimension** on
> its own. Its speed curve accelerates, peaks and decelerates; its trajectory
> curvature is as high as a human's, sometimes higher.
>
> What it cannot beat is nine dimensions at once: its pressure varies too little,
> its jitter is too regular, and the phone it drives barely moves. Something is
> always out of place.
>
> **Any single feature can be imitated by a sufficiently good machine.
> Only the combination pins one down.**
