import pandas as pd

DEVIATION_ROUND = 4

ERR_EMPTY_DF = "DataFrame не содержит данных для определения всплеска."


class SpikeAgent:

    def detect_spike(self, daily_df: pd.DataFrame) -> dict:
        if daily_df.empty:
            raise ValueError(ERR_EMPTY_DF)
        worst_row = self._find_worst_day(daily_df)
        deviation = self._calc_deviation(daily_df, worst_row["score"])
        return {
            "date": str(worst_row["date"]),
            "score": float(worst_row["score"]),
            "deviation": deviation,
        }

    def _find_worst_day(self, df: pd.DataFrame) -> pd.Series:
        idx = df["score"].idxmin()
        return df.loc[idx]

    def _calc_deviation(self, df: pd.DataFrame, spike_score: float) -> float:
        mean_score = df["score"].mean()
        deviation = abs(spike_score - mean_score)
        return round(deviation, DEVIATION_ROUND)
