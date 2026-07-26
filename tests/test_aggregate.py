import unittest

from gesture_behavior_classifier.aggregate import aggregate_predictions


class AggregateTests(unittest.TestCase):
    def test_insufficient_samples(self):
        rows = [
            {
                "gesture_type": "TAP",
                "test_site": "室内",
                "phone_status": "平放手机",
                "test_method": "点击固定位置",
                "predicted_tool": "自动化脚本-屏幕录制",
                "confidence": 0.9,
            }
            for _ in range(10)
        ]
        result = aggregate_predictions(rows, {"sample_policy": {"tap_min_samples": 50}})[0]
        self.assertEqual(result["sample_status"], "样本不足")
        self.assertEqual(result["final_predicted_tool"], "样本不足")

    def test_enough_samples_majority(self):
        rows = [
            {
                "gesture_type": "SWIPE",
                "test_site": "室内",
                "phone_status": "平放手机",
                "test_method": "随机位置向上滑动",
                "predicted_tool": "自动化脚本-代码开发",
                "confidence": 0.85,
            }
            for _ in range(35)
        ]
        result = aggregate_predictions(rows, {"sample_policy": {"swipe_min_samples": 30, "stable_majority_ratio": 0.6}})[0]
        self.assertEqual(result["sample_status"], "可判定")
        self.assertEqual(result["final_predicted_tool"], "自动化脚本-代码开发")


if __name__ == "__main__":
    unittest.main()
