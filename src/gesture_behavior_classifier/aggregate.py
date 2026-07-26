from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def min_samples_for_group(rows: list[dict[str, Any]], config: dict[str, Any], override: int | None = None) -> int:
    if override is not None:
        return override
    policy = config.get("sample_policy", {})
    gesture_types = {str(row.get("gesture_type", "")) for row in rows}
    if gesture_types == {"SWIPE"}:
        return int(policy.get("swipe_min_samples", policy.get("default_min_samples", 50)))
    if gesture_types == {"TAP"}:
        return int(policy.get("tap_min_samples", policy.get("default_min_samples", 50)))
    return int(policy.get("default_min_samples", 50))


def classify_prediction_group(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    min_samples_override: int | None = None,
) -> dict[str, Any]:
    policy = config.get("sample_policy", {})
    n = len(rows)
    min_samples = min_samples_for_group(rows, config, min_samples_override)
    counter = Counter(str(row.get("predicted_tool", "未知")) for row in rows)
    top_tool, top_count = counter.most_common(1)[0] if counter else ("未知", 0)
    top_ratio = top_count / n if n else 0.0
    avg_confidence = (
        sum(float(row.get("confidence", 0) or 0) for row in rows if str(row.get("predicted_tool", "未知")) == top_tool) / top_count
        if top_count
        else 0.0
    )

    if n < min_samples:
        final_tool = "样本不足"
        status = "样本不足"
        confidence_level = "低"
        conclusion = f"当前分组只有 {n} 条，低于最低样本量 {min_samples}，不建议输出正式类别。"
    elif top_ratio < float(policy.get("mixed_majority_ratio_below", 0.45)):
        final_tool = "混合/不确定"
        status = "不稳定"
        confidence_level = "低"
        conclusion = "最高类别占比偏低，可能混合了多种行为或当前规则证据冲突。"
    elif top_ratio >= float(policy.get("stable_majority_ratio", 0.60)) and avg_confidence >= 0.58:
        final_tool = top_tool
        status = "可判定"
        confidence_level = "高" if top_ratio >= 0.75 and avg_confidence >= 0.70 else "中"
        conclusion = f"最高类别为 {top_tool}，占比 {top_ratio * 100:.2f}%，组内一致性满足最低样本量要求。"
    else:
        final_tool = top_tool
        status = "弱判定"
        confidence_level = "中低"
        conclusion = f"最高类别为 {top_tool}，但占比或平均置信度一般，建议补充样本后复核。"

    return {
        "sample_count": n,
        "min_required_samples": min_samples,
        "sample_status": status,
        "final_predicted_tool": final_tool,
        "group_confidence_level": confidence_level,
        "top_single_tool": top_tool,
        "top_single_count": top_count,
        "top_single_ratio_pct": round(top_ratio * 100.0, 2),
        "top_single_avg_confidence": round(avg_confidence, 4),
        "prediction_distribution": "; ".join(f"{name}:{count}" for name, count in counter.most_common()),
        "conclusion": conclusion,
    }


def aggregate_predictions(
    predictions: list[dict[str, Any]],
    config: dict[str, Any],
    group_by: list[str] | None = None,
    min_samples_override: int | None = None,
) -> list[dict[str, Any]]:
    if group_by is None:
        group_by = list(config.get("sample_policy", {}).get("default_group_by", ["gesture_type"]))

    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in predictions:
        key = tuple(str(row.get(field, "")) for field in group_by)
        groups[key].append(row)

    output = []
    for key, rows in sorted(groups.items()):
        result = {
            "group_by_fields": ",".join(group_by),
            "group_key": " | ".join(f"{field}={key[index]}" for index, field in enumerate(group_by)),
        }
        result.update({field: key[index] for index, field in enumerate(group_by)})
        result.update(classify_prediction_group(rows, config, min_samples_override))
        output.append(result)
    return output
