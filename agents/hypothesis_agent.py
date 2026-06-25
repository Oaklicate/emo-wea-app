import pandas as pd

STORM_HIGH_THRESHOLD = 0.5
NEGATIVITY_SHARE_THRESHOLD = 0.4
ACTIVITY_SPIKE_RATIO = 1.5
TOPICS_NARROW_THRESHOLD = 10
VOLATILITY_HIGH_THRESHOLD = 0.3

H1_NAME = "Высокий Storm Index сопровождается ростом негативных сообщений"
H2_NAME = "Эмоциональные всплески совпадают с повышенной активностью аудитории"
H3_NAME = "Доминирующие темы связаны с периодами эмоциональных изменений"

CONFIRMED = "✅ Подтверждена"
PARTIAL = "⚠ Частично подтверждена"
REJECTED = "❌ Не подтверждена"


class HypothesisAgent:

    def validate(
        self,
        daily: pd.DataFrame,
        storm_index: float,
        topics: list,
    ) -> list:
        return [
            self._h1_storm_and_negativity(daily, storm_index),
            self._h2_spikes_and_activity(daily),
            self._h3_topics_and_volatility(daily, topics),
        ]

    def _h1_storm_and_negativity(
        self,
        daily: pd.DataFrame,
        storm_index: float,
    ) -> tuple:
        if storm_index < STORM_HIGH_THRESHOLD:
            return H1_NAME, REJECTED
        neg_share = self._negative_share(daily)
        if neg_share >= NEGATIVITY_SHARE_THRESHOLD:
            return H1_NAME, CONFIRMED
        return H1_NAME, PARTIAL

    def _h2_spikes_and_activity(self, daily: pd.DataFrame) -> tuple:
        if "count" not in daily.columns or daily.empty:
            return H2_NAME, PARTIAL
        mean_count = daily["count"].mean()
        worst_idx = daily["score"].idxmin()
        spike_count = daily.loc[worst_idx, "count"]
        if spike_count >= mean_count * ACTIVITY_SPIKE_RATIO:
            return H2_NAME, CONFIRMED
        return H2_NAME, REJECTED

    def _h3_topics_and_volatility(
        self,
        daily: pd.DataFrame,
        topics: list,
    ) -> tuple:
        volatility = self._score_volatility(daily)
        has_topics = bool(topics) and len(topics) <= TOPICS_NARROW_THRESHOLD
        if has_topics and volatility >= VOLATILITY_HIGH_THRESHOLD:
            return H3_NAME, CONFIRMED
        if has_topics or volatility >= VOLATILITY_HIGH_THRESHOLD:
            return H3_NAME, PARTIAL
        return H3_NAME, REJECTED

    def _negative_share(self, daily: pd.DataFrame) -> float:
        if daily.empty:
            return 0.0
        return float((daily["score"] < 0).sum()) / len(daily)

    def _score_volatility(self, daily: pd.DataFrame) -> float:
        if daily.empty or len(daily) < 2:
            return 0.0
        return float(daily["score"].std())
