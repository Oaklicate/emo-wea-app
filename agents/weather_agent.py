import pandas as pd


class WeatherAgent:

    def calculate_weather(self, df):

        daily = (
            df.groupby("date")["score"]
            .mean()
            .reset_index()
        )

        current_index = daily["score"].iloc[-1]

        if current_index > 0.6:
            weather = "☀️ Ясно"

        elif current_index > 0.2:
            weather = "⛅ Переменная облачность"

        elif current_index > -0.2:
            weather = "🌥 Облачно"

        elif current_index > -0.6:
            weather = "🌧 Дождь"

        else:
            weather = "⛈ Шторм"

        return daily, current_index, weather