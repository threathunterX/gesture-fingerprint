from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .aggregate import aggregate_predictions
from .features import compute_features
from .io_utils import dump_json_text, load_json, read_csv_rows, write_csv_rows
from .report import write_markdown_report
from .rules import classify_gesture, summarize_predictions


DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default_rules.json"


FEATURE_COLUMNS = [
    "gesture_index",
    "gesture_type",
    "test_site",
    "phone_status",
    "test_method",
    "start_x",
    "start_y",
    "end_x",
    "end_y",
    "duration_ms",
    "avg_pressure",
    "max_pressure",
    "pressure_fluctuation_coeff",
    "contact_area_mean",
    "speed_mean_positive_px_s",
    "speed_fluctuation_coeff",
    "path_redundancy_rate",
    "summary_avg_curvature",
    "linear_accel_magnitude",
    "gyro_magnitude",
    "click_group_count",
    "click_bbox_w",
    "click_bbox_h",
    "click_unique_xy_ratio_pct",
    "click_dominant_xy_ratio_pct",
    "click_space_pattern",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="识别未知点击/滑动数据来自真人、脚本或硬件工具的可能类别。")
    parser.add_argument("--summary-csv", required=True, help="手势级汇总 CSV，例如 数据汇总_20260723V2.csv")
    parser.add_argument("--trajectory-csv", default="", help="轨迹点 CSV，例如 数据汇总_20260723V2_trajectory.csv")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="规则配置 JSON")
    parser.add_argument("--min-samples", type=int, default=None, help="覆盖最低样本量；未指定时 TAP 默认 50、SWIPE 默认 30")
    parser.add_argument(
        "--group-by",
        default="",
        help="正式判定的分组字段，逗号分隔；默认只按 gesture_type 分组，适合未知测试数据",
    )
    return parser


def prediction_rows(features: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for feature in features:
        prediction = classify_gesture(feature, config)
        row = dict(feature)
        row.update(
            {
                "predicted_tool": prediction["predicted_tool"],
                "confidence": prediction["confidence"],
                "confidence_level": prediction["confidence_level"],
                "top_score": prediction["top_score"],
                "second_score": prediction["second_score"],
                "score_detail": dump_json_text(prediction["score_detail"]),
                "evidence": "；".join(prediction["evidence"]),
            }
        )
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config = load_json(args.config)
    summary_rows = read_csv_rows(args.summary_csv)
    trajectory_rows = read_csv_rows(args.trajectory_csv) if args.trajectory_csv else []

    features = compute_features(summary_rows, trajectory_rows, config)
    predictions = prediction_rows(features, config)
    summary = summarize_predictions(predictions)
    group_by = [item.strip() for item in args.group_by.split(",") if item.strip()] or None
    grouped = aggregate_predictions(predictions, config, group_by=group_by, min_samples_override=args.min_samples)

    extra_feature_columns = list(features[0].keys()) if features else []
    feature_fieldnames = FEATURE_COLUMNS + [key for key in extra_feature_columns if key not in FEATURE_COLUMNS]
    prediction_fieldnames = [
        "gesture_index",
        "gesture_type",
        "test_site",
        "phone_status",
        "test_method",
        "predicted_tool",
        "confidence",
        "confidence_level",
        "top_score",
        "second_score",
        "evidence",
        "score_detail",
    ] + [key for key in FEATURE_COLUMNS if key not in {"gesture_index", "gesture_type", "test_site", "phone_status", "test_method"}]

    write_csv_rows(output_dir / "手势特征明细.csv", features, feature_fieldnames)
    write_csv_rows(output_dir / "手势识别结果.csv", predictions, prediction_fieldnames)
    grouped_fieldnames = []
    for row in grouped:
        for key in row:
            if key not in grouped_fieldnames:
                grouped_fieldnames.append(key)
    write_csv_rows(output_dir / "分组正式判定.csv", grouped, grouped_fieldnames)
    write_csv_rows(
        output_dir / "批次识别汇总.csv",
        summary,
        ["gesture_type", "phone_status", "sample_count", "top_predicted_tool", "top_predicted_ratio_pct", "prediction_distribution"],
    )
    write_markdown_report(output_dir / "识别报告.md", predictions, summary, grouped)

    print(f"完成：{len(predictions)} 条手势")
    print(f"输出目录：{output_dir}")
    print(f"- {output_dir / '手势识别结果.csv'}")
    print(f"- {output_dir / '分组正式判定.csv'}")
    print(f"- {output_dir / '批次识别汇总.csv'}")
    print(f"- {output_dir / '识别报告.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
