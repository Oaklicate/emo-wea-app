import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

FORECAST_HORIZON = 7
SCORE_MIN = -1.0
SCORE_MAX = 1.0
STORM_INDEX_MAX = 1.0
STORM_INDEX_ROUND = 2

ERR_EMPTY_DF = "DataFrame не содержит данных для прогноза."


class ForecastAgent:

    def forecast(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        if daily_df.empty:
            raise ValueError(ERR_EMPTY_DF)
        x_train, y_train = self._build_features(daily_df)
        model = self._fit_model(x_train, y_train)
        x_future = self._future_features(len(daily_df))
        predictions = self._predict(model, x_future)
        return pd.DataFrame({
            "day": range(1, FORECAST_HORIZON + 1),
            "forecast_score": predictions,
        })

    def storm_index(self, forecast_df: pd.DataFrame) -> float:
        mean_abs = abs(forecast_df["forecast_score"].mean())
        value = min(mean_abs, STORM_INDEX_MAX)
        return round(value, STORM_INDEX_ROUND)

    def _build_features(self, df: pd.DataFrame):
        x = np.arange(len(df)).reshape(-1, 1)
        y = df["score"].values
        return x, y

    def _future_features(self, n_known: int) -> np.ndarray:
        return np.arange(n_known, n_known + FORECAST_HORIZON).reshape(-1, 1)

    def _fit_model(self, x: np.ndarray, y: np.ndarray) -> LinearRegression:
        model = LinearRegression()
        model.fit(x, y)
        return model

    def _predict(self, model: LinearRegression, x: np.ndarray) -> np.ndarray:
        raw = model.predict(x)
        return np.clip(raw, SCORE_MIN, SCORE_MAX)
