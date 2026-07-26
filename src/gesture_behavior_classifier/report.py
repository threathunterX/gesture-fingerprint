from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


def write_markdown_report(
    path: str | Path,
    predictions: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    group_rows: list[dict[str, Any]] | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    counter = Counter(str(row.get("predicted_tool", "未知")) for row in predictions)
    total = sum(counter.values())
    lines = [
        "# 未知点击/滑动行为识别报告",
        "",
        f"- 手势总数：{total}",
        f"- 预测类别数：{len(counter)}",
        "",
        "## 总体预测分布",
        "",
        "| 预测类别 | 数量 | 占比 |",
        "|---|---:|---:|",
    ]
    for name, count in counter.most_common():
        ratio = count / total * 100.0 if total else 0.0
        lines.append(f"| {name} | {count} | {ratio:.2f}% |")

    if group_rows is not None:
        lines.extend(
            [
                "",
                "## 分组正式判定",
                "",
                "| 分组 | 样本数 | 最低样本量 | 状态 | 最终判断 | 组内主类别占比 | 说明 |",
                "|---|---:|---:|---|---|---:|---|",
            ]
        )
        for row in group_rows:
            lines.append(
                "| {group_key} | {sample_count} | {min_required_samples} | {sample_status} | {final_predicted_tool} | {top_single_ratio_pct:.2f}% | {conclusion} |".format(
                    **row
                )
            )

    lines.extend(
        [
            "",
            "## 按动作与手机状态汇总",
            "",
            "| 动作类型 | 手机状态 | 样本数 | 主要预测 | 主要预测占比 | 分布 |",
            "|---|---|---:|---|---:|---|",
        ]
    )
    for row in summary_rows:
        lines.append(
            "| {gesture_type} | {phone_status} | {sample_count} | {top_predicted_tool} | {top_predicted_ratio_pct:.2f}% | {prediction_distribution} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## 使用说明",
            "",
            "- 正式判断优先看 `分组正式判定.csv`；单条手势预测随机性较高，只建议作为规则命中明细。",
            "- 默认正式分组只使用 `gesture_type`，因为正式未知数据通常不会包含 `test_site`、`phone_status`、`test_method`。",
            "- 默认最低样本量：TAP 为 50 条，SWIPE 为 30 条；可以用命令行 `--min-samples` 覆盖。",
            "- 本项目采用规则评分，不是机器学习模型；输出的 `evidence` 字段会列出命中的主要规则。",
            "- `手持手机-行走` 下线性加速度和陀螺仪会整体抬高，报告中只把它们作为场景证据，不建议单独定性工具。",
            "- 点击空间特征是批次级特征，样本量太少时会输出 `样本不足`，此时应更多依赖压力、接触面积和轨迹特征。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
