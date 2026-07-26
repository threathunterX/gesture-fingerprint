import unittest

from gesture_behavior_classifier.rules import classify_gesture


def config():
    import json
    from pathlib import Path

    # 从 cli 取默认配置路径，避免测试与实际打包位置分叉
    from gesture_behavior_classifier.cli import DEFAULT_CONFIG

    return json.loads(Path(DEFAULT_CONFIG).read_text(encoding="utf-8"))


class RuleTests(unittest.TestCase):
    def test_code_script_swipe_rule(self):
        feature = {
            "gesture_type": "SWIPE",
            "contact_area_mean": 0,
            "avg_pressure": 1,
            "pressure_fluctuation_coeff": 0,
            "speed_fluctuation_coeff": 0.01,
            "path_redundancy_rate": 0.0,
            "summary_avg_curvature": 0.0001,
        }
        result = classify_gesture(feature, config())
        self.assertEqual(result["predicted_tool"], "自动化脚本-代码开发")

    def test_mouse_pressure_rule(self):
        feature = {
            "gesture_type": "SWIPE",
            "contact_area_mean": 0,
            "avg_pressure": 0.5,
            "pressure_fluctuation_coeff": 1,
            "speed_mean_positive_px_s": 500,
            "speed_fluctuation_coeff": 0.5,
        }
        result = classify_gesture(feature, config())
        self.assertEqual(result["predicted_tool"], "鼠标点击器")


if __name__ == "__main__":
    unittest.main()
