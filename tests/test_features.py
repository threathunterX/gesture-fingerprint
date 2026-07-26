import unittest

from gesture_behavior_classifier.features import compute_features


class FeatureTests(unittest.TestCase):
    def test_pressure_and_contact_features(self):
        summary = [
            {
                "gesture_index": "g1",
                "gesture_type": "TAP",
                "start_x": "10",
                "start_y": "20",
                "end_x": "10",
                "end_y": "20",
                "avg_pressure": "1",
                "linear_x": "3",
                "linear_y": "4",
                "linear_z": "0",
                "gyro_x": "0",
                "gyro_y": "0",
                "gyro_z": "2",
                "test_method": "点击固定位置",
            }
        ]
        trajectory = [
            {"gesture_index": "g1", "point_index": "0", "x": "10", "y": "20", "pressure": "1", "touch_major": "10", "touch_minor": "20", "vx_px_s": "0", "vy_px_s": "0"},
            {"gesture_index": "g1", "point_index": "1", "x": "10", "y": "20", "pressure": "1", "touch_major": "10", "touch_minor": "20", "vx_px_s": "0", "vy_px_s": "0"},
        ]
        config = {"click_space": {"min_group_size": 1}}
        features = compute_features(summary, trajectory, config)
        self.assertEqual(len(features), 1)
        self.assertEqual(round(features[0]["linear_accel_magnitude"], 4), 5.0)
        self.assertEqual(round(features[0]["gyro_magnitude"], 4), 2.0)
        self.assertEqual(features[0]["pressure_fluctuation_coeff"], 0.0)
        self.assertEqual(round(features[0]["contact_area_mean"], 4), 157.0796)

    def test_swipe_path_redundancy(self):
        summary = [{"gesture_index": "s1", "gesture_type": "SWIPE", "avg_pressure": "1"}]
        trajectory = [
            {"gesture_index": "s1", "point_index": "0", "x": "0", "y": "0", "pressure": "1", "touch_major": "0", "touch_minor": "0", "vx_px_s": "0", "vy_px_s": "0"},
            {"gesture_index": "s1", "point_index": "1", "x": "3", "y": "4", "pressure": "1", "touch_major": "0", "touch_minor": "0", "vx_px_s": "3", "vy_px_s": "4"},
            {"gesture_index": "s1", "point_index": "2", "x": "6", "y": "8", "pressure": "1", "touch_major": "0", "touch_minor": "0", "vx_px_s": "3", "vy_px_s": "4"},
        ]
        features = compute_features(summary, trajectory, {"click_space": {}})
        self.assertEqual(features[0]["path_length_px"], 10.0)
        self.assertEqual(features[0]["straight_distance_px"], 10.0)
        self.assertEqual(features[0]["path_redundancy_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
