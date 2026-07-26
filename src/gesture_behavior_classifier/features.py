from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from typing import Any


MISSING = ""


def to_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except ValueError:
        return default


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def pstdev(values: list[float]) -> float | None:
    if len(values) < 2:
        return 0.0 if values else None
    return statistics.pstdev(values)


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def first_nonempty(row: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key, "")
        if str(value).strip():
            return str(value).strip()
    return ""


def deduplicate_summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        gesture_index = row.get("gesture_index", "")
        if gesture_index and gesture_index in seen:
            continue
        if gesture_index:
            seen.add(gesture_index)
        deduped.append(row)
    return deduped


def group_trajectory_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("gesture_index", "")].append(row)
    for points in grouped.values():
        points.sort(key=lambda r: to_float(r.get("point_index"), 0.0) or 0.0)
    return grouped


def magnitude(row: dict[str, str], keys: tuple[str, str, str]) -> float | None:
    values = [to_float(row.get(key)) for key in keys]
    if any(value is None for value in values):
        return None
    return math.sqrt(sum((value or 0.0) ** 2 for value in values))


def path_length(points: list[dict[str, str]]) -> float | None:
    if len(points) < 2:
        return None
    total = 0.0
    prev_x = to_float(points[0].get("x"))
    prev_y = to_float(points[0].get("y"))
    if prev_x is None or prev_y is None:
        return None
    for point in points[1:]:
        x = to_float(point.get("x"))
        y = to_float(point.get("y"))
        if x is None or y is None:
            continue
        total += math.hypot(x - prev_x, y - prev_y)
        prev_x, prev_y = x, y
    return total


def straight_distance(row: dict[str, str], points: list[dict[str, str]]) -> float | None:
    if len(points) >= 2:
        sx = to_float(points[0].get("x"))
        sy = to_float(points[0].get("y"))
        ex = to_float(points[-1].get("x"))
        ey = to_float(points[-1].get("y"))
    else:
        sx = to_float(row.get("start_x"))
        sy = to_float(row.get("start_y"))
        ex = to_float(row.get("end_x"))
        ey = to_float(row.get("end_y"))
    if None in (sx, sy, ex, ey):
        return None
    return math.hypot((ex or 0.0) - (sx or 0.0), (ey or 0.0) - (sy or 0.0))


def classify_click_space(group: dict[str, Any], config: dict[str, Any]) -> str:
    thresholds = config.get("click_space", {})
    min_group_size = thresholds.get("min_group_size", 20)
    if group.get("click_group_count", 0) < min_group_size:
        return "样本不足"

    bbox_w = group.get("click_bbox_w")
    bbox_h = group.get("click_bbox_h")
    unique_ratio = group.get("click_unique_xy_ratio_pct")
    dominant_ratio = group.get("click_dominant_xy_ratio_pct")
    if None in (bbox_w, bbox_h, unique_ratio, dominant_ratio):
        return "不可判断"

    if (
        unique_ratio < thresholds.get("fixed_unique_ratio_pct_max", 5.0)
        or dominant_ratio > thresholds.get("fixed_dominant_ratio_pct_min", 30.0)
    ):
        return "固定点重复"

    if (
        thresholds.get("offset_bbox_w_min", 50.0) <= bbox_w <= thresholds.get("offset_bbox_w_max", 300.0)
        and thresholds.get("offset_bbox_h_min", 50.0) <= bbox_h <= thresholds.get("offset_bbox_h_max", 600.0)
        and dominant_ratio < thresholds.get("offset_dominant_ratio_pct_max", 1.0)
    ):
        return "局部坐标偏移"

    if (
        bbox_w > thresholds.get("random_bbox_w_min", 450.0)
        and bbox_h > thresholds.get("random_bbox_h_min", 800.0)
        and unique_ratio > thresholds.get("random_unique_ratio_pct_min", 85.0)
        and dominant_ratio < thresholds.get("random_dominant_ratio_pct_max", 1.0)
    ):
        return "全屏随机"

    if bbox_w < thresholds.get("fixed_small_bbox_max", 30.0) and bbox_h < thresholds.get("fixed_small_bbox_max", 30.0):
        return "小范围固定抖动"
    return "混合/业务目标分布"


def compute_click_space_groups(features: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in features:
        if item.get("gesture_type") != "TAP":
            continue
        key = item.get("test_method") or "__ALL_TAP__"
        groups[key].append(item)

    result: dict[str, dict[str, Any]] = {}
    for key, rows in groups.items():
        coords = []
        xs = []
        ys = []
        for row in rows:
            x = to_float(row.get("start_x"))
            y = to_float(row.get("start_y"))
            if x is None or y is None:
                continue
            coords.append((round(x), round(y)))
            xs.append(x)
            ys.append(y)

        if not coords:
            stats = {
                "click_group_key": key,
                "click_group_count": 0,
                "click_bbox_w": None,
                "click_bbox_h": None,
                "click_x_std": None,
                "click_y_std": None,
                "click_unique_xy_ratio_pct": None,
                "click_dominant_xy_ratio_pct": None,
                "click_bbox_area": None,
            }
        else:
            counter = Counter(coords)
            count = len(coords)
            bbox_w = max(xs) - min(xs)
            bbox_h = max(ys) - min(ys)
            stats = {
                "click_group_key": key,
                "click_group_count": count,
                "click_bbox_w": bbox_w,
                "click_bbox_h": bbox_h,
                "click_x_std": pstdev(xs),
                "click_y_std": pstdev(ys),
                "click_unique_xy_ratio_pct": len(counter) / count * 100.0,
                "click_dominant_xy_ratio_pct": max(counter.values()) / count * 100.0,
                "click_bbox_area": bbox_w * bbox_h,
            }
        stats["click_space_pattern"] = classify_click_space(stats, config)
        result[key] = stats
    return result


def compute_features(
    summary_rows: list[dict[str, str]],
    trajectory_rows: list[dict[str, str]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    summary_rows = deduplicate_summary_rows(summary_rows)
    points_by_gesture = group_trajectory_rows(trajectory_rows)
    result: list[dict[str, Any]] = []

    for row in summary_rows:
        gesture_index = row.get("gesture_index", "")
        points = points_by_gesture.get(gesture_index, [])
        feature: dict[str, Any] = {
            "gesture_index": gesture_index,
            "method": row.get("method", ""),
            "target_element": row.get("target_element", ""),
            "gesture_type": row.get("gesture_type", ""),
            "test_site": row.get("test_site", ""),
            "phone_status": row.get("phone_status", ""),
            "test_method": row.get("test_method", ""),
            "test_tool": row.get("test_tool", ""),
            "start_x": to_float(row.get("start_x")),
            "start_y": to_float(row.get("start_y")),
            "end_x": to_float(row.get("end_x")),
            "end_y": to_float(row.get("end_y")),
            "duration_ms": to_float(row.get("duration_ms")),
            "avg_pressure": to_float(row.get("avg_pressure")),
            "max_pressure": to_float(row.get("max_pressure")),
            "summary_touch_major": to_float(row.get("touch_major")),
            "summary_touch_minor": to_float(row.get("touch_minor")),
            "summary_total_distance": to_float(row.get("total_distance")),
            "summary_avg_curvature": to_float(row.get("avg_curvature")),
            "trajectory_points_summary": to_float(row.get("trajectory_points")),
            "linear_accel_magnitude": magnitude(row, ("linear_x", "linear_y", "linear_z")),
            "gyro_magnitude": magnitude(row, ("gyro_x", "gyro_y", "gyro_z")),
        }

        pressures = [value for value in (to_float(p.get("pressure")) for p in points) if value is not None]
        pressure_mean = mean(pressures)
        pressure_std = pstdev(pressures)
        feature["pressure_mean_points"] = pressure_mean
        feature["pressure_std_points"] = pressure_std
        feature["pressure_fluctuation_coeff"] = safe_div(pressure_std, pressure_mean)

        areas = []
        for point in points:
            major = to_float(point.get("touch_major"))
            minor = to_float(point.get("touch_minor"))
            if major is None or minor is None:
                continue
            areas.append(math.pi / 4.0 * major * minor)
        if not areas:
            major = feature["summary_touch_major"]
            minor = feature["summary_touch_minor"]
            if major is not None and minor is not None:
                areas.append(math.pi / 4.0 * major * minor)
        feature["contact_area_mean"] = mean(areas)
        feature["contact_area_median"] = median(areas)
        feature["contact_area_max"] = max(areas) if areas else None

        speeds = []
        for point in points:
            vx = to_float(point.get("vx_px_s"))
            vy = to_float(point.get("vy_px_s"))
            if vx is None or vy is None:
                continue
            speed = math.hypot(vx, vy)
            if speed > 0:
                speeds.append(speed)
        speed_mean = mean(speeds)
        speed_std = pstdev(speeds)
        feature["speed_mean_positive_px_s"] = speed_mean
        feature["speed_std_positive_px_s"] = speed_std
        feature["speed_fluctuation_coeff"] = safe_div(speed_std, speed_mean)
        feature["speed_positive_point_count"] = len(speeds)

        length = path_length(points)
        straight = straight_distance(row, points)
        feature["path_length_px"] = length
        feature["straight_distance_px"] = straight
        if straight is not None and straight >= 10 and length is not None:
            feature["path_redundancy_rate"] = length / straight - 1.0
        else:
            feature["path_redundancy_rate"] = None

        curvatures = [value for value in (to_float(p.get("curvature")) for p in points) if value is not None]
        feature["trajectory_curvature_mean"] = mean(curvatures)
        feature["trajectory_curvature_max"] = max(curvatures) if curvatures else None
        result.append(feature)

    click_groups = compute_click_space_groups(result, config)
    for item in result:
        if item.get("gesture_type") == "TAP":
            key = item.get("test_method") or "__ALL_TAP__"
            item.update(click_groups.get(key, {}))
        else:
            item.update(
                {
                    "click_group_key": "",
                    "click_group_count": "",
                    "click_bbox_w": "",
                    "click_bbox_h": "",
                    "click_x_std": "",
                    "click_y_std": "",
                    "click_unique_xy_ratio_pct": "",
                    "click_dominant_xy_ratio_pct": "",
                    "click_bbox_area": "",
                    "click_space_pattern": "",
                }
            )
    return result
