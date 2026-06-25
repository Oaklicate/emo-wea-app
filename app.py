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
from agents.schema_agent import SchemaAgent



def configure_page():
    st.set_page_config(
        page_title="EmoScope",
        page_icon="🌦️",
        layout="wide",
    )
    st.title("🌦️ EmoScope")
    st.caption("AI-платформа анализа эмоционального климата онлайн-сообществ")


def render_sidebar():
    with st.sidebar:
        st.header("📂 Источник данных")
        uploaded_file = st.file_uploader(
            "Загрузите данные",
            type=["csv", "json", "toml"],
        )
        st.markdown("---")
        st.markdown("### Поддерживаемые источники")
        st.success("✅ CSV")
        st.success("✅ JSON")
        st.success("✅ TOML")
        st.info("🚧 Telegram API (скоро)")
        st.info("🚧 VK API (скоро)")
        st.markdown("---")
        st.markdown(
            "**EmoScope** анализирует сообщения сообщества, "
            "определяет эмоциональный климат, выявляет триггеры "
            "и строит прогноз эмоционального шторма."
        )
    return uploaded_file


def run_analysis(uploaded_file):
    
    sentiment_agent = SentimentAgent()
    weather_agent = WeatherAgent()
    forecast_agent = ForecastAgent()
    spike_agent = SpikeAgent()
    narrative_agent = NarrativeAgent()
    visualization_agent = VisualizationAgent()
    report_agent = ReportAgent()
    hypothesis_agent = HypothesisAgent()

    with st.spinner("ИИ выполняет анализ..."):
        try:
            df_raw = DataAgent.load_file(uploaded_file)
            df = sentiment_agent.analyze(df_raw)
            daily, current_index, weather = weather_agent.calculate_weather(df)
            forecast_df = forecast_agent.forecast(daily)
            storm_index = forecast_agent.storm_index(forecast_df)
            spike = spike_agent.detect_spike(daily)
            topics = narrative_agent.get_topics(df)
            graph = visualization_agent.build_emotion_graph(df, weather)
            fig = visualization_agent.draw_graph(graph)
            report = report_agent.generate(weather, current_index, storm_index, spike, topics)
            hypotheses = hypothesis_agent.validate(daily, storm_index, topics)
        except Exception as e:
            st.error(str(e))
            st.stop()

    return df_raw, df, daily, current_index, weather, forecast_df, storm_index, spike, topics, fig, report, hypotheses


def render_kpi(weather, current_index, storm_index, spike):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌦 Погода", weather)
    with col2:
        st.metric("📈 Эмоциональный индекс", round(current_index, 2))
    with col3:
        st.metric("⚠ Storm Index", storm_index)
    with col4:
        st.metric("⚡ Spike Score", round(spike["score"], 2))


def render_tabs(df_raw, df, daily, forecast_df, topics, fig, report, hypotheses):
    tab_overview, tab_emotions, tab_forecast, tab_map, tab_report, tab_hypotheses = st.tabs([
        "🗂 Обзор",
        "😶 Эмоции",
        "📈 Прогноз",
        "🕸 Карта",
        "🧠 Отчёт",
        "🧪 Гипотезы",
    ])

    with tab_overview:
        st.subheader("Предпросмотр исходных данных")
        st.dataframe(df_raw.head())
        st.subheader("Результаты анализа")
        st.dataframe(df.head(20))
        st.subheader("Динамика эмоционального индекса")
        st.line_chart(daily.set_index("date")["score"])

    with tab_emotions:
        st.subheader("Основные темы")
        for word, freq in topics:
            st.write(f"• {word} ({freq})")
        st.subheader("Эмоциональная динамика")
        st.line_chart(daily.set_index("date")["score"])

    with tab_forecast:
        st.subheader("Прогноз эмоциональной погоды")
        st.dataframe(forecast_df)
        st.line_chart(forecast_df.set_index("day")["forecast_score"])

    with tab_map:
        st.subheader("Карта эмоций")
        st.pyplot(fig)

    with tab_report:
        st.subheader("Аналитический отчёт")
        st.info(report)

    with tab_hypotheses:
        st.subheader("Проверка гипотез")
        for hypothesis, result in hypotheses:
            st.markdown(f"### {result}")
            st.write(hypothesis)


def main():
    configure_page()
    uploaded_file = render_sidebar()

    if not uploaded_file:
        st.info("Загрузите файл данных в боковой панели для начала анализа.")
        st.stop()

    results = run_analysis(uploaded_file)
    df_raw, df, daily, current_index, weather, forecast_df, storm_index, spike, topics, fig, report, hypotheses = results

    with st.sidebar:
        st.markdown("---")
        st.success(f"📋 Загружено записей: {len(df_raw)}")

    st.markdown("---")
    render_kpi(weather, current_index, storm_index, spike)
    st.markdown("---")
    render_tabs(df_raw, df, daily, forecast_df, topics, fig, report, hypotheses)


main()