DIVIDER = "━" * 36

INDEX_HIGH_POS = 0.7
INDEX_MOD_POS = 0.3
INDEX_MOD_NEG = -0.3
INDEX_HIGH_NEG = -0.7

STORM_LOW = 0.3
STORM_MEDIUM = 0.6
STORM_HIGH = 0.85

WEATHER_DESCRIPTIONS = {
    "☀️": "В сообществе наблюдается устойчивый положительный эмоциональный фон.",
    "⛅": "Эмоциональная обстановка в сообществе умеренно позитивная с отдельными негативными сигналами.",
    "🌥": "В сообществе преобладает нейтральный или слабо выраженный эмоциональный фон.",
    "🌧": "В сообществе наблюдается преобладание негативных реакций.",
    "⛈": "Сообщество переживает выраженный эмоциональный кризис с высокой долей негатива.",
}
WEATHER_DEFAULT = "Эмоциональное состояние сообщества определено как «{weather}»."

TOPICS_MAX = 7


class ReportAgent:

    def generate(self, weather, current_index, storm_index, spike, topics):
        sections = [
            self._section("ОБЩЕЕ СОСТОЯНИЕ", self._build_weather_summary(weather)),
            self._section("📊 ЭМОЦИОНАЛЬНЫЙ ИНДЕКС", self._build_index_summary(current_index)),
            self._section("⚠ ПРОГНОЗ И STORM INDEX", self._build_storm_summary(storm_index)),
            self._section("📈 ВСПЛЕСКИ", self._build_spike_summary(spike)),
            self._section("💬 КЛЮЧЕВЫЕ ТЕМЫ", self._build_topics_summary(topics)),
            self._section("🧠 ВЫВОД", self._build_conclusion(weather, current_index, storm_index, spike)),
        ]
        return "\n\n".join(sections)

    def _section(self, title, body):
        return f"{DIVIDER}\n{title}\n{DIVIDER}\n{body}"

    def _build_weather_summary(self, weather):
        description = WEATHER_DESCRIPTIONS.get(
            weather,
            WEATHER_DEFAULT.format(weather=weather),
        )
        return f"Погода: {weather}\n{description}"

    def _build_index_summary(self, current_index):
        value = round(current_index, 2)
        if value >= INDEX_HIGH_POS:
            interpretation = "Очень высокий позитивный уровень — сообщество демонстрирует активную вовлечённость и поддержку."
        elif value >= INDEX_MOD_POS:
            interpretation = "Умеренно позитивный уровень — преобладают конструктивные и дружественные высказывания."
        elif value > INDEX_MOD_NEG:
            interpretation = "Нейтральное состояние — эмоции сбалансированы, явного перевеса нет."
        elif value > INDEX_HIGH_NEG:
            interpretation = "Умеренно негативный уровень — фиксируется рост недовольства и критики."
        else:
            interpretation = "Высокий негативный уровень — сообщество находится в состоянии стресса или конфликта."
        return f"Текущее значение: {value}\n{interpretation}"

    def _build_storm_summary(self, storm_index):
        if storm_index <= STORM_LOW:
            risk = "низкий"
            detail = "Вероятность эмоционального шторма в ближайшем периоде минимальна."
        elif storm_index <= STORM_MEDIUM:
            risk = "средний"
            detail = "Есть признаки нарастания напряжённости. Рекомендуется мониторинг."
        elif storm_index <= STORM_HIGH:
            risk = "высокий"
            detail = "Высокая вероятность эмоционального шторма. Необходимо превентивное вмешательство."
        else:
            risk = "критический"
            detail = "Критический уровень. Сообщество находится на пороге или в состоянии эмоционального шторма."
        return f"Storm Index: {storm_index} — риск {risk}.\n{detail}"

    def _build_spike_summary(self, spike):
        date = spike.get("date", "неизвестная дата")
        score = round(spike.get("score", 0), 2)
        return (
            f"Наиболее выраженный эмоциональный всплеск зарегистрирован {date} "
            f"с интенсивностью {score}.\n"
            "Этот момент мог быть вызван значимым событием или волной реакций внутри сообщества."
        )

    def _build_topics_summary(self, topics):
        if not topics:
            return "Ключевые темы не определены."
        lines = [f"  • {word} ({freq})" for word, freq in topics[:TOPICS_MAX]]
        return "Наиболее обсуждаемые темы:\n" + "\n".join(lines)

    def _build_conclusion(self, weather, current_index, storm_index, spike):
        tone = "позитивный" if current_index >= INDEX_MOD_POS else ("нейтральный" if current_index > INDEX_MOD_NEG else "негативный")
        urgency = "не требует немедленного вмешательства" if storm_index <= STORM_MEDIUM else "требует оперативного внимания модераторов"
        return (
            f"Эмоциональный климат сообщества в анализируемый период — {tone}. "
            f"Storm Index составляет {storm_index}, что {urgency}. "
            f"Пиковая активность зафиксирована {spike.get('date', 'в неизвестный период')}. "
            "Для поддержания здорового климата рекомендуется регулярный мониторинг и своевременная реакция на резкие изменения индекса."
        )