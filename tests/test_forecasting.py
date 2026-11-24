"""Tests for utility consumption forecasts."""
import unittest
from unittest.mock import patch

import pandas as pd

from konsumo import forecasting


class ForecastingTests(unittest.TestCase):
    def setUp(self):
        self.history = pd.Series(
            [10.0, 12.0, 11.0, 13.0, 12.0, 14.0, 15.0],
            index=pd.date_range("2026-01-01", periods=7, freq="D"),
        )

    @patch("konsumo.forecasting.daily_series")
    def test_requires_at_least_seven_days_of_history(self, daily_series):
        daily_series.return_value = self.history.iloc[:6]
        with self.assertRaisesRegex(ValueError, "at least 7 days"):
            forecasting.forecast_daily("electricity", ":memory:", user_id=1)

    @patch("konsumo.forecasting.daily_series")
    def test_returns_thirty_non_negative_daily_predictions(self, daily_series):
        daily_series.return_value = self.history
        predicted, metadata = forecasting.forecast_daily("electricity", ":memory:", user_id=1)
        self.assertEqual(len(predicted), 30)
        self.assertEqual(predicted.index[0], pd.Timestamp("2026-01-08"))
        self.assertEqual(predicted.index[-1], pd.Timestamp("2026-02-06"))
        self.assertTrue((predicted >= 0).all())
        self.assertIn("mae", metadata)
        self.assertEqual(metadata["method"], "moving-average + linear trend")

    @patch("konsumo.forecasting.daily_series")
    def test_downward_trend_is_clamped_at_zero(self, daily_series):
        daily_series.return_value = pd.Series(
            [100.0, 80.0, 60.0, 40.0, 20.0, 5.0, 1.0],
            index=pd.date_range("2026-01-01", periods=7, freq="D"),
        )
        predicted, _ = forecasting.forecast_daily("water", ":memory:", user_id=1)
        self.assertTrue((predicted >= 0).all())
        self.assertEqual(float(predicted.min()), 0.0)


if __name__ == "__main__":
    unittest.main()
