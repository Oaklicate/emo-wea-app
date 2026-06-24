import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression


class ForecastAgent:

    def forecast(self, daily_df):

        df = daily_df.copy()

        df = df.reset_index(drop=True)

        X = np.arange(len(df)).reshape(-1, 1)

        y = df["score"].values

        model = LinearRegression()

        model.fit(X, y)

        future_X = np.arange(
            len(df),
            len(df) + 7
        ).reshape(-1, 1)

        forecast = model.predict(
            future_X
        )
        forecast = np.clip(
    forecast,
    -1,
    1
)

        forecast_df = pd.DataFrame(
            {
                "day": range(1, 8),
                "forecast_score": forecast
            }
        )

        return forecast_df
    
    def storm_index(self, forecast_df):

        value = abs(
            forecast_df[
                "forecast_score"
            ].mean()
        )

        value = min(value, 1)

        return round(value, 2)