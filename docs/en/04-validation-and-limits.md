# 04 · Validation & limits

**English** · [中文](../04-验证与局限.md)

## Blind test

Five characteristic methods, each captured fresh and **taking no part in rule
design**, then classified blind:

| Actual device | Engine's distribution | Correct / total |
|---|---|---:|
| Human — index finger, swipe up | human 50 | 50 / 50 |
| Screen-recording playback | playback 50 | 50 / 50 |
| Human — thumb, swipe up | human 53 / unknown 1 | 53 / 54 |
| Mouse clicker | mouse clicker 39 / HID 11 | 39 / 50 |
| Robotic arm | robotic arm 48 / unknown 18 | 48 / 66 |

> ⚠️ **These are not accuracy figures.** Each group holds only a few dozen samples;
> even a clean sweep has a confidence-interval lower bound around 93%. Change the
> device batch or the phone model and the numbers move. Their job is to **locate the
> errors**, not to promise performance.

**No cross-category errors occurred** — a human was never classified as a machine,
and a machine was never classified as a human. Every error stayed within one
category or degraded to *unknown*. That is currently the most trustworthy property
of the method.

---

## Error attribution

### Mouse clicker: 11 of 50 read as HID

Split those 50 and the correct and incorrect groups are almost indistinguishable:

| | Contact area | Mean pressure | Mean speed | Speed variability |
|---|---:|---:|---:|---:|
| The 39 correct | 0 | **0.9444** | 546 | 0.326 |
| The 11 wrong | 0 | **0.9524** | 541 | 0.397 |

The only difference is pressure — and the boundary `pressure_one_min = 0.95` sits
**right on the mode of this batch**. Anything at 0.9524 falls into the
"pressure pinned at 1" software/HID branch; anything at 0.9444 does not.

More importantly: **the rule that says "a mouse clicker's pressure is typically 0.5"
never fired once on this validation data** — the measured value was 0.94. The 39
correct verdicts rest entirely on the single rule "no contact + speed < 800 px/s".
Whatever produced the 0.5 figure is tied to a device batch or a ROM, and **cannot be
treated as a stable feature**.

### Robotic arm: 18 of 66 returned unknown

The robotic arm's features all sit between a human's and a script's, and the rule
that identifies it is an AND of several conditions over fairly narrow ranges. These
18 samples matched the arm on most dimensions but fell outside the range on one, so
the rule did not fire at all.

The single unknown in the human set is the same story — contact area and pressure
both landed just under the human band.

What this exposes is a **gap in the layering**: the rules jump straight from the
coarse question "was there real physical contact?" to a specific device model, with
nothing in between. A gesture that clearly belongs to the physical-contact class but
matches no known model ought to be reported as *physical-contact class, model
unknown* — instead it lands in the same *unknown* bucket as data with no signal at all.

### Improvement directions

Tracked in [Issues](../../../../issues). Bring your own captures and open an issue
or PR. Two kinds of contribution matter most:

- **New device samples** (label `new-device`) — the value of this project is a
  function of how many real tools it covers
- **Per-model calibration data** (label `calibration`) — the shipped thresholds have
  only ever been validated on our lab devices

---

## Limits

### 1. Not a real-time blocker

A formal verdict needs ≥30 swipes or ≥50 taps. It produces an **account- or
session-level classification** and cannot stop a single request. The right place for
it is behind your existing blocking pipeline, doing classification and attribution —
not in place of it.

### 2. Requires client-side instrumentation

Pressure, contact area and per-point trajectories can only be captured inside the
app. Not one of the required fields exists in gateway logs, CDN logs or server-side
API logs.

### 3. Thresholds need per-model calibration

`contact_area > 15000` and `speed > 4000 px/s` are absolute values, tightly coupled
to screen DPI, touch driver and ROM. The shipped thresholds come from our lab
devices; **a new phone model must be recalibrated**.

The 0.5-vs-0.94 pressure contradiction above is the most direct illustration of this
problem.

### 4. Two sensor dimensions need context

The linear-acceleration and gyroscope rules depend on a phone-state label
(handheld / flat / walking). Production telemetry rarely carries that field, in which
case those two dimensions sit out and **7 dimensions are actually in play**.

Walking and subway scenarios also contaminate both dimensions
(see [02 · The nine dimensions](./02-nine-dimensions.md)); they should be
down-weighted there.

### 5. A rule engine, not a trained model

Upside: every verdict is explainable, auditable, and can go straight into a report.
Downside: thresholds must be recalibrated per device and capture environment, and
the engine will not adapt to a new device on its own.

### 6. `confidence` is not a probability

The reported `confidence` is a monotone transform of the rule score, not a posterior
probability. **Do not read it as "99% sure".** It is only useful for ranking within a
single batch, and is not comparable across batches.
