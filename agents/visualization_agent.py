import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

MAX_MESSAGES = 50
LABEL_MAX_LEN = 18
LAYOUT_SEED = 42
LAYOUT_K = 2.5

NODE_COLORS = {
    "Позитив": "#4caf50",
    "Негатив": "#f44336",
    "Нейтрально": "#9e9e9e",
    "weather": "#42a5f5",
    "message": "#ffe082",
}

NODE_SIZES = {
    "weather": 4000,
    "emotion": 2500,
    "message": 800,
}

EMOTIONS = {
    "positive": "Позитив",
    "negative": "Негатив",
    "neutral": "Нейтрально",
}


def _emotion_label(score):
    if score > 0:
        return EMOTIONS["positive"]
    if score < 0:
        return EMOTIONS["negative"]
    return EMOTIONS["neutral"]


def _short_label(text, max_len=LABEL_MAX_LEN):
    text = str(text).strip()
    return text[:max_len] + "…" if len(text) > max_len else text


class VisualizationAgent:

    def build_emotion_graph(self, df, weather):
        G = nx.DiGraph()
        G.add_node(weather, kind="weather")

        for emotion in EMOTIONS.values():
            G.add_node(emotion, kind="emotion")
            G.add_edge(weather, emotion)

        if df.empty:
            return G

        sample = df.head(MAX_MESSAGES)
        for idx, row in sample.iterrows():
            label = f"#{idx} {_short_label(row['text'])}"
            emotion = _emotion_label(row["score"])
            G.add_node(label, kind="message")
            G.add_edge(emotion, label)

        return G

    def draw_graph(self, G):
        fig, ax = plt.subplots(figsize=(14, 9))
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")

        pos = nx.spring_layout(G, seed=LAYOUT_SEED, k=LAYOUT_K)

        node_colors = self._get_node_colors(G)
        node_sizes = self._get_node_sizes(G)
        labels = {node: node for node in G.nodes()}

        self._draw_edges(G, pos, ax)
        self._draw_nodes(G, pos, node_colors, node_sizes, ax)
        self._draw_labels(G, pos, labels, node_sizes, ax)

        legend_patches = [
            mpatches.Patch(color=NODE_COLORS["Позитив"], label="Позитив"),
            mpatches.Patch(color=NODE_COLORS["Негатив"], label="Негатив"),
            mpatches.Patch(color=NODE_COLORS["Нейтрально"], label="Нейтрально"),
            mpatches.Patch(color=NODE_COLORS["weather"], label="Погода"),
            mpatches.Patch(color=NODE_COLORS["message"], label="Сообщение"),
        ]
        ax.legend(handles=legend_patches, loc="upper left", facecolor="#2e2e3e", labelcolor="white")
        ax.axis("off")
        plt.tight_layout()
        return fig

    def _draw_edges(self, G, pos, ax):
        nx.draw_networkx_edges(
            G, pos,
            edge_color="#555577",
            arrows=True,
            arrowsize=12,
            width=0.8,
            ax=ax,
        )

    def _draw_nodes(self, G, pos, colors, sizes, ax):
        nx.draw_networkx_nodes(
            G, pos,
            node_color=colors,
            node_size=sizes,
            ax=ax,
        )

    def _draw_labels(self, G, pos, labels, sizes, ax):
        font_sizes = {
            node: 9 if G.nodes[node].get("kind") == "message" else 11
            for node in G.nodes()
        }
        for node, (x, y) in pos.items():
            ax.text(
                x, y, labels[node],
                fontsize=font_sizes[node],
                ha="center", va="center",
                color="black",
                fontweight="bold",
                wrap=True,
            )

    def _get_node_colors(self, G):
        result = []
        for node in G.nodes():
            kind = G.nodes[node].get("kind")
            if kind == "weather":
                result.append(NODE_COLORS["weather"])
            elif kind == "message":
                result.append(NODE_COLORS["message"])
            else:
                result.append(NODE_COLORS.get(node, "#cccccc"))
        return result

    def _get_node_sizes(self, G):
        result = []
        for node in G.nodes():
            kind = G.nodes[node].get("kind")
            result.append(NODE_SIZES.get(kind, NODE_SIZES["message"]))
        return result