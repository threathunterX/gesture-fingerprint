# 01 · Experiment method

**English** · [中文](../01-实验方法.md)

## What was tested

### Hardware — all bought off the shelf

| Device | How it works | Price (RMB) |
|---|---|---:|
| Robotic arm | Camera captures the screen → image recognition → arm physically taps and swipes | **1535** |
| Screen-swiper B | Physical motor rotation drives the swipe | 79 |
| Capacitive clicker | A capacitor discharges into one fixed point on the glass | 61.9 |
| OTG clicker | Wired OTG + HID protocol + custom script | 58 |
| Mouse clicker | Bluetooth + HID protocol carrying mouse / touch events | 39 |
| Screen-swiper A | Physical motor rotation drives the swipe | 37.5 |
| Auto-swipe/liker | Bluetooth + HID protocol | 34.9 |
| HID Bluetooth clicker | Bluetooth + HID protocol | 18.3 |
| | **Total** | **1863.6** |

> All of these are sold openly on mainstream e-commerce platforms; the cheapest
> costs about as much as a takeaway meal.
> **This document deliberately provides no purchasing links.**

### Software baselines

| Type | How it works |
|---|---|
| Hand-written script | Injects synthetic gesture events through the Android accessibility service |
| Screen-recording playback | Records a real human session and replays it, also via accessibility injection |

**Why is hardware harder to detect than software?**

Software injects through the Android accessibility service, and an app can check
whether accessibility is enabled, whether the device is rooted, and whether it is
running in a virtual machine. **What hardware evades is that class of
*environment* check.** Four of the eight devices above (HID Bluetooth, OTG, mouse
clicker, auto-swipe/liker) speak the HID protocol, so to the system they are simply
an external mouse — a natively supported device type with nothing to flag.

Worth stating plainly: **"producing a real touch" is not the purchasing motive.**
Those four HID devices report a contact area of exactly 0 — no real touch at all —
and they are the cheapest and most widespread of the lot. The genuine contact area
that a physical tip produces is a *by-product* of how capacitive clickers and
robotic arms happen to get the job done.

And it is precisely that by-product which forms the first split in the detection
method: **environment checks and behavioural checks are two different things.** An
HID device gets past "has this phone been modified?" but not past "did anything
actually touch the glass?" — a contact area of exactly 0, or a placeholder constant
of 1, is what the system inevitably reports for a non-touch input source, and it
cannot be faked.

### Engine classes vs. test devices

| Engine output class | Device tested |
|---|---|
| `HID` | HID Bluetooth clicker / OTG clicker |
| `auto-swipe/liker` | Auto-swipe + clicker |
| `screen-swiper A` | Auto screen-swiper, type 1 |
| `screen-swiper B` | Auto screen-swiper, type 2 |
| others | same name |

---

## Scenarios

Five phone states. The point was to give the sensor dimensions a baseline, and to
check whether a human stays separable across postures:

| Scenario | Why |
|---|---|
| Indoor · flat on a desk | The desk absorbs the force of a press |
| Indoor · upright in a stand | Far easier to nudge than a phone lying flat |
| Indoor · handheld, seated | Closest to everyday use |
| Indoor · handheld, walking | Introduces body motion |
| Subway · handheld, seated | Introduces external vibration |

## Tasks

| Action | Variants |
|---|---|
| Tap | Fixed position / random position / fixed position with coordinate jitter |
| Swipe | Fixed-position upward / random-position upward; the human set additionally splits thumb vs. index finger |
| Combined | Swipe up + like + save (imitating a real short-video interaction chain) |

These variants exist to produce the *tap spatial distribution* feature:
fixed-point repetition, small rectangular jitter, and wide random spread each
distribute very differently between a human and a tool.

## Sample sizes

Two rounds:

| | Repetitions per task | Purpose |
|---|---|---|
| Round 1 | 20–50 | Find out which dimensions discriminate at all |
| Round 2 | **300–500** | Scale up, re-check round 1, freeze thresholds |

**Four dimensions produced conclusions in round 2 that contradicted round 1**
(path redundancy, mean curvature, speed variability, and some sensor scenarios).
Small samples were simply not stable — which is the direct reason the engine
enforces a minimum sample size (≥30 swipes, ≥50 taps) before issuing a formal verdict.

Round 2 valid samples per tool (counted on the pressure-variability dimension,
i.e. gestures carrying complete per-point data):

| Tool | Valid gestures |
|---|---:|
| Hand-written script | 20,961 |
| Human | 19,354 |
| Mouse clicker | 15,219 |
| Screen-recording playback | 9,919 |
| Robotic arm | 5,118 |
| Capacitive clicker | 1,939 |
| Auto-swipe/liker | 1,044 |
| Screen-swiper A | 1,023 |
| Screen-swiper B | 809 |
| **Total** | **75,386** (HID excluded) |

---

## Data collection

A purpose-built Android collector (`gesture-collector-v2.apk`, on the
[Releases](../../../../releases) page) writes one summary row per gesture and
logs trajectory points every ~10 ms.

### Gesture summary CSV

```
gesture_index, method, target_element, gesture_type,
start_x, start_y, end_x, end_y, timestamp_ms, duration_ms,
avg_pressure, max_pressure, touch_major, touch_minor, avg_size,
max_speed_x, max_speed_y, max_speed, total_distance, max_acceleration, avg_curvature,
accel_x/y/z, gyro_x/y/z, gravity_x/y/z, linear_x/y/z, mag_x/y/z,
pointer_count, trajectory_points
```

### Trajectory point CSV

```
gesture_index, point_index, x, y, pressure,
touch_major, touch_minor, vx_px_s, vy_px_s, curvature
```

**The trajectory CSV is required.** Pressure variability, contact area, speed
variability and path redundancy all derive from per-point data; a summary-only
input loses most of the discriminative power.

### Derived feature definitions

| Feature | Computed as |
|---|---|
| Contact area | `π/4 × touch_major × touch_minor`, per point, then averaged |
| Pressure variability | Std. dev. / mean of `pressure` within one gesture |
| Speed variability | Std. dev. / mean of instantaneous speed within one gesture (points with speed > 0 only) |
| Path redundancy | `actual path length / straight-line distance − 1` (see caution below) |
| Linear acceleration magnitude | `√(linear_x² + linear_y² + linear_z²)` |
| Gyroscope magnitude | `√(gyro_x² + gyro_y² + gyro_z²)` |

> ⚠️ **Two conventions for path redundancy.**
> The original analysis writes "redundancy = 1" meaning
> `path length / straight-line distance = 1`, i.e. no detour at all.
> The code's `path_redundancy_rate` is **that ratio minus 1**, so no detour is 0.
> "A human travels 4.8% farther than the straight line" is 1.048 in the analysis
> convention and 0.048 in the code convention.
> **Every threshold in `default_rules.json` uses the code convention.**
