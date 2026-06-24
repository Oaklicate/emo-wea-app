class SpikeAgent:

    def detect_spike(self, daily_df):

        worst_row = daily_df.loc[
            daily_df["score"].idxmin()
        ]

        return {
            "date": str(worst_row["date"]),
            "score": float(worst_row["score"])
        }