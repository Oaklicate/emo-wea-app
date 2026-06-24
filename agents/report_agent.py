class ReportAgent:

    def generate(
        self,
        weather,
        current_index,
        storm_index,
        spike,
        topics
    ):

        topic_list = ", ".join(
            [
                word
                for word, _
                in topics[:5]
            ]
        )

        return f"""
Текущее состояние сообщества: {weather}.

Эмоциональный индекс составляет {round(current_index, 2)}.

Storm Index равен {storm_index}.

Наиболее выраженный эмоциональный всплеск зафиксирован {spike['date']}.

Основные темы обсуждения:
{topic_list}.

Прогноз указывает на сохранение текущего эмоционального тренда.
"""