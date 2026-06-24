import networkx as nx
import matplotlib.pyplot as plt


class VisualizationAgent:

    def build_emotion_graph(
        self,
        df,
        weather
    ):

        G = nx.DiGraph()

        G.add_node(weather)

        for _, row in df.iterrows():

            topic = row["text"][:25]

            if row["score"] > 0:
                emotion = "Позитив"

            elif row["score"] < 0:
                emotion = "Негатив"

            else:
                emotion = "Нейтрально"

            G.add_node(topic)
            G.add_node(emotion)

            G.add_edge(topic, emotion)
            G.add_edge(emotion, weather)

        return G

    def draw_graph(self, G):

        fig, ax = plt.subplots(
            figsize=(12, 8)
        )

        pos = nx.spring_layout(
            G,
            seed=42
        )

        colors = []

        for node in G.nodes():

            if node == "Позитив":
                colors.append("green")

            elif node == "Негатив":
                colors.append("red")

            elif node == "Нейтрально":
                colors.append("gray")

            else:
                colors.append("skyblue")

        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=colors,
            node_size=3000,
            font_size=8,
            ax=ax
        )

        return fig