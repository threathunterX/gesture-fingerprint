from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any


def value(row: dict[str, Any], key: str) -> float | None:
    raw = row.get(key)
    if raw in ("", None):
        return None
    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric):
        return None
    return numeric


def between(number: float | None, low: float, high: float) -> bool:
    return number is not None and low <= number <= high


def le(number: float | None, limit: float) -> bool:
    return number is not None and number <= limit


def ge(number: float | None, limit: float) -> bool:
    return number is not None and number >= limit


def classify_gesture(feature: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    thresholds = config.get("feature_thresholds", {})
    classes = config.get("classes", [])
    scores = {class_name: 0.0 for class_name in classes}
    evidence: dict[str, list[str]] = defaultdict(list)

    def add(class_name: str, points: float, reason: str) -> None:
        scores[class_name] = scores.get(class_name, 0.0) + points
        evidence[class_name].append(reason)

    gesture_type = str(feature.get("gesture_type", ""))
    phone_status = str(feature.get("phone_status", ""))
    test_site = str(feature.get("test_site", ""))
    click_space_pattern = str(feature.get("click_space_pattern", ""))

    contact = value(feature, "contact_area_mean")
    avg_pressure = value(feature, "avg_pressure")
    pressure_fluct = value(feature, "pressure_fluctuation_coeff")
    speed = value(feature, "speed_mean_positive_px_s")
    speed_fluct = value(feature, "speed_fluctuation_coeff")
    redundancy = value(feature, "path_redundancy_rate")
    curvature = value(feature, "summary_avg_curvature")
    linear = value(feature, "linear_accel_magnitude")
    gyro = value(feature, "gyro_magnitude")

    no_contact = le(contact, thresholds["contact_area_zero_max"])
    physical_contact = ge(contact, thresholds["physical_contact_min"])
    pressure_one = between(avg_pressure, thresholds["pressure_one_min"], thresholds["pressure_one_max"])
    pressure_mouse = between(avg_pressure, thresholds["pressure_mouse_min"], thresholds["pressure_mouse_max"])
    pressure_static = le(pressure_fluct, thresholds["pressure_static_coeff_max"])

    if no_contact and pressure_one:
        for name in ["自动化脚本-代码开发", "自动化脚本-屏幕录制", "HID", "自动滑屏点赞器"]:
            add(name, 1.5, "接触面积接近 0 且平均压力接近 1，符合注入/非真实接触类基础特征")
    if no_contact and pressure_mouse:
        add("鼠标点击器", 4.0, "接触面积接近 0 且平均压力接近 0.5，符合鼠标点击器压力模式")
    if physical_contact:
        for name in ["真人", "机械臂", "刷屏器一", "刷屏器二", "电容点击器"]:
            add(name, 1.2, "存在明显接触面积，进入真实接触/物理触控分支")

    if pressure_static and pressure_one and no_contact:
        for name in ["自动化脚本-代码开发", "自动化脚本-屏幕录制", "HID", "自动滑屏点赞器"]:
            add(name, 1.0, "逐点压力波动接近 0，且压力恒定为 1")

    if pressure_fluct is not None and pressure_fluct >= 0.7 and no_contact:
        add("鼠标点击器", 2.0, "无接触面积但压力波动系数很高，偏向鼠标点击器")

    if gesture_type == "SWIPE":
        if no_contact and pressure_one and le(speed_fluct, thresholds["code_speed_fluct_max"]) and le(redundancy, thresholds["swipe_straight_redundancy_max"]) and le(curvature, thresholds["low_curvature_max"]):
            add("自动化脚本-代码开发", 5.0, "滑动速度波动极低、路径近直线、曲率极低，符合代码开发脚本")
        if no_contact and pressure_one and le(speed_fluct, thresholds["screen_speed_fluct_max"]) and between(redundancy, thresholds["screen_record_redundancy_min"], thresholds["screen_record_redundancy_max"]):
            add("自动化脚本-屏幕录制", 4.5, "路径冗余率落在录制轨迹常见区间，且无真实接触")
        if no_contact and pressure_one and ge(speed, thresholds["auto_swiper_speed_min"]):
            add("自动滑屏点赞器", 5.5, "滑动平均速度极高且无真实接触，符合自动滑屏点赞器")
        if no_contact and le(speed, thresholds["mouse_speed_max"]):
            add("鼠标点击器", 3.5, "无接触面积且滑动平均速度偏低，符合鼠标点击器")
        if no_contact and pressure_one and ge(speed_fluct, thresholds["hid_speed_fluct_min"]) and le(redundancy, thresholds["swipe_straight_redundancy_max"]):
            add("HID", 2.2, "HID 常见压力恒 1、无接触面积，但速度波动不一定极低")

        if ge(contact, thresholds["human_contact_area_min"]) and ge(avg_pressure, thresholds["human_pressure_min"]) and ge(pressure_fluct, thresholds["human_pressure_fluct_min"]):
            add("真人", 3.5, "接触面积较大、压力更自然且存在压力波动，符合真人触控")
        if ge(contact, thresholds["human_contact_area_min"]) and ge(speed, thresholds["human_speed_min"]) and between(speed_fluct, 0.25, 0.85):
            add("真人", 2.5, "滑动速度较高且速度波动处于自然范围")

        if between(contact, thresholds["mechanical_contact_area_min"], thresholds["mechanical_contact_area_max"]) and le(avg_pressure, thresholds["mechanical_pressure_max"]) and ge(speed_fluct, 0.55):
            add("机械臂", 3.5, "接触面积中等、压力偏低、速度波动偏高，符合机械臂/物理工具特征")
        if between(contact, thresholds["brush1_contact_area_min"], thresholds["brush1_contact_area_max"]) and between(avg_pressure, thresholds["brush1_pressure_min"], thresholds["brush1_pressure_max"]) and ge(speed_fluct, thresholds["brush1_speed_fluct_min"]):
            add("刷屏器一", 5.0, "接触面积、压力和极高速度波动符合刷屏器一")
        if between(contact, thresholds["brush2_contact_area_min"], thresholds["brush2_contact_area_max"]) and between(avg_pressure, thresholds["brush2_pressure_min"], thresholds["brush2_pressure_max"]) and between(speed, thresholds["brush2_speed_min"], thresholds["brush2_speed_max"]):
            add("刷屏器二", 5.0, "接触面积高、压力约 0.27、滑动速度较慢，符合刷屏器二")

    if gesture_type == "TAP":
        if between(contact, thresholds["capacitor_contact_area_min"], thresholds["capacitor_contact_area_max"]) and between(avg_pressure, thresholds["capacitor_pressure_min"], thresholds["capacitor_pressure_max"]) and le(pressure_fluct, thresholds["capacitor_pressure_fluct_max"]):
            add("电容点击器", 4.5, "点击接触面积和压力稳定，符合电容点击器")
        if ge(contact, thresholds["human_contact_area_min"]) and ge(avg_pressure, thresholds["human_pressure_min"]) and ge(pressure_fluct, thresholds["human_pressure_fluct_min"]):
            add("真人", 3.2, "点击接触面积较大且压力存在自然波动")
        if between(contact, thresholds["mechanical_contact_area_min"], thresholds["mechanical_contact_area_max"]) and le(avg_pressure, thresholds["mechanical_pressure_max"]):
            add("机械臂", 2.8, "点击接触面积中等且压力偏低，符合机械臂物理触控")

        if click_space_pattern == "固定点重复":
            add("自动化脚本-屏幕录制", 1.6, "点击空间表现为固定点高度重复")
            add("鼠标点击器", 1.2, "点击空间表现为固定点高度重复")
            add("自动化脚本-代码开发", 1.0, "点击空间表现为少量固定坐标簇")
        elif click_space_pattern == "小范围固定抖动":
            add("HID", 1.4, "点击空间是小范围固定抖动")
            add("机械臂", 1.2, "点击空间是小范围固定抖动")
        elif click_space_pattern == "局部坐标偏移":
            add("HID", 1.6, "点击空间为局部坐标偏移，符合 HID/偏移工具")
            add("机械臂", 1.2, "点击空间为局部坐标偏移，符合机械臂偏移执行")
            add("自动化脚本-代码开发", 1.0, "点击空间为局部坐标偏移，也可能来自代码随机偏移")
        elif click_space_pattern == "全屏随机":
            add("真人", 0.8, "点击空间为全屏随机，仅作为弱证据")
            add("自动化脚本-代码开发", 0.5, "程序也可生成全屏随机，点击空间仅作为弱证据")

    if phone_status == "手持手机-坐着":
        if ge(linear, thresholds["hand_sitting_linear_human_min"]) and physical_contact:
            add("真人", 1.5, "手持坐着时线性加速度较高且存在真实接触，增强真人证据")
        if ge(gyro, thresholds["hand_sitting_gyro_human_min"]) and physical_contact:
            add("真人", 2.0, "手持坐着时陀螺仪合量较高且存在真实接触，强辅助真人")
    if phone_status == "竖放手机":
        if ge(linear, thresholds["vertical_linear_human_min"]) and physical_contact:
            add("真人", 1.2, "竖放手机线性加速度偏高且存在真实接触，增强真人证据")
        if ge(gyro, thresholds["vertical_gyro_human_min"]) and physical_contact:
            add("真人", 1.5, "竖放手机陀螺仪合量偏高且存在真实接触，增强真人证据")
    if test_site == "地铁" and phone_status == "手持手机-坐着" and ge(gyro, thresholds["metro_gyro_human_min"]) and physical_contact:
        add("真人", 1.2, "地铁手持坐着时陀螺仪仍较高，作为真人辅助证据")

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_class, best_score = ranked[0] if ranked else ("未知", 0.0)
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    unknown_below = config.get("confidence", {}).get("unknown_score_below", 2.5)
    if best_score < unknown_below:
        best_class = "未知"

    margin = max(0.0, best_score - second_score)
    confidence = min(0.99, max(0.05, 0.25 + best_score / 12.0 + margin / 10.0))
    if best_class == "未知":
        confidence = min(confidence, 0.45)
    high_min = config.get("confidence", {}).get("high_min", 0.78)
    medium_min = config.get("confidence", {}).get("medium_min", 0.58)
    confidence_level = "高" if confidence >= high_min else "中" if confidence >= medium_min else "低"

    return {
        "predicted_tool": best_class,
        "confidence": round(confidence, 4),
        "confidence_level": confidence_level,
        "top_score": round(best_score, 4),
        "second_score": round(second_score, 4),
        "score_detail": {name: round(score, 4) for name, score in ranked if score > 0},
        "evidence": evidence.get(best_class, []) if best_class != "未知" else [],
    }


def summarize_predictions(predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in predictions:
        key = (str(row.get("gesture_type", "")), str(row.get("phone_status", "")))
        groups[key][str(row.get("predicted_tool", "未知"))] += 1

    summary = []
    for (gesture_type, phone_status), counter in sorted(groups.items()):
        total = sum(counter.values())
        top_tool, top_count = counter.most_common(1)[0]
        summary.append(
            {
                "gesture_type": gesture_type,
                "phone_status": phone_status,
                "sample_count": total,
                "top_predicted_tool": top_tool,
                "top_predicted_ratio_pct": round(top_count / total * 100.0, 2) if total else 0,
                "prediction_distribution": "; ".join(f"{name}:{count}" for name, count in counter.most_common()),
            }
        )
    return summary
