import streamlit as st

from agents.data_agent import DataAgent
from agents.sentiment_agent import SentimentAgent
from agents.weather_agent import WeatherAgent
from agents.forecast_agent import ForecastAgent
from agents.narrative_agent import NarrativeAgent
from agents.spike_agent import SpikeAgent
from agents.report_agent import ReportAgent
from agents.visualization_agent import VisualizationAgent
from agents.hypothesis_agent import HypothesisAgent




st.set_page_config(
    page_title="Эмоциональная погода сообщества",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Эмоциональная погода сообщества")

st.markdown(
    """
    Анализ эмоционального климата онлайн-сообществ.
    """
)

uploaded_file = st.file_uploader(
    "Загрузите CSV, JSON или TOML",
    type=["csv", "json", "toml"]
)

if uploaded_file:

    try:

        df = DataAgent.load_file(
            uploaded_file
        )

        st.success(
            f"Файл успешно загружен. Записей: {len(df)}"
        )

        st.subheader("Предпросмотр данных")

        st.dataframe(df.head())
        sentiment_agent = SentimentAgent()

        with st.spinner("ИИ анализирует комментарии..."):

            df = sentiment_agent.analyze(df)

        st.subheader("Результаты анализа")

        st.dataframe(
            df.head(20)
        )
    except Exception as e:

        st.error(str(e))

    weather_agent = WeatherAgent()

    daily, current_index, weather = (
        weather_agent.calculate_weather(df)
    )

    st.divider()

    st.subheader("Текущая эмоциональная погода")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Эмоциональный индекс",
            round(current_index, 2)
        )

    with col2:
        st.metric(
            "Погода",
            weather
        )

    st.divider()

    st.subheader(
        "Динамика эмоционального индекса"
    )

    st.line_chart(
        daily.set_index("date")["score"]
    )


    forecast_agent = ForecastAgent()

    forecast_df = forecast_agent.forecast(
        daily
    )

    st.divider()

    st.subheader(
        "Прогноз эмоциональной погоды"
    )

    st.dataframe(
        forecast_df
    )

    st.line_chart(
        forecast_df.set_index("day")[
            "forecast_score"
        ]
    )

    storm_index = (
    forecast_agent.storm_index(
        forecast_df
    )
    )   

    st.metric(
        "Storm Index",
        storm_index
    )
    spike_agent = SpikeAgent()

    spike = spike_agent.detect_spike(
        daily
    )

    st.divider()

    st.subheader(
        "⚡ Эмоциональный всплеск"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Дата",
            spike["date"]
        )

    with col2:
        st.metric(
            "Индекс",
            round(
                spike["score"],
                2
            )
        )
    narrative_agent = NarrativeAgent()

    topics = narrative_agent.get_topics(
        df
    )

    st.divider()

    st.subheader(
        "Основные триггеры и темы"
    )

    for word, freq in topics:

        st.write(
            f"• {word} ({freq})"
        )
    report_agent = ReportAgent()

    report = report_agent.generate(
        weather,
        current_index,
        storm_index,
        spike,
        topics
    )

    st.divider()

    st.subheader(
        "🧠 Аналитическая сводка"
    )

    st.info(report)

    st.divider()

    st.subheader(
        "🕸 Карта эмоциональных волн"
    )

    visual_agent = VisualizationAgent()

    graph = visual_agent.build_emotion_graph(
        df,
        weather
    )

    fig = visual_agent.draw_graph(
        graph
    )

    st.pyplot(fig)

    st.divider()

    st.subheader(
        "🧪 Проверка гипотез"
    )

    hypothesis_agent = (
        HypothesisAgent()
    )

    hypotheses = (
        hypothesis_agent.validate(
            daily,
            storm_index,
            topics
        )
    )

    for hypothesis, result in hypotheses:

        st.markdown(
            f"""
    **Гипотеза**

    {hypothesis}

    **Статус**

    {result}
    """
    )