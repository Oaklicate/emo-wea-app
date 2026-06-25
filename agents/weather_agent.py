import pandas as pd

INDEX_SUNNY = 0.6
INDEX_PARTLY_CLOUDY = 0.2
INDEX_CLOUDY = -0.2
INDEX_RAIN = -0.6

WEATHER_SUNNY = "☀️ Ясно"
WEATHER_PARTLY_CLOUDY = "⛅ Переменная облачность"
WEATHER_CLOUDY = "🌥 Облачно"
WEATHER_RAIN = "🌧 Дождь"
WEATHER_STORM = "⛈ Шторм"

ERR_EMPTY_DF = "DataFrame не содержит данных для расчёта погоды."


class WeatherAgent:

    def calculate_weather(self, df: pd.DataFrame):
        if df.empty:
            raise ValueError(ERR_EMPTY_DF)
        daily = self._calc_daily_index(df)
        current_index = self._calc_current_index(daily)
        weather = self._calc_weather_label(current_index)
        return daily, current_index, weather

    def _calc_daily_index(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby("date")["score"]
            .mean()
            .reset_index()
        )

    def _calc_current_index(self, daily: pd.DataFrame) -> float:
        return float(daily["score"].iloc[-1])

    def _calc_weather_label(self, index: float) -> str:
        if index > INDEX_SUNNY:
            return WEATHER_SUNNY
        if index > INDEX_PARTLY_CLOUDY:
            return WEATHER_PARTLY_CLOUDY
        if index > INDEX_CLOUDY:
            return WEATHER_CLOUDY
        if index > INDEX_RAIN:
            return WEATHER_RAIN
        return WEATHER_STORM
