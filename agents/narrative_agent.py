from sklearn.feature_extraction.text import CountVectorizer


class NarrativeAgent:

    def get_topics(
        self,
        df,
        top_n=10
    ):

        texts = (
            df["text"]
            .astype(str)
            .tolist()
        )

        vectorizer = CountVectorizer(
            stop_words="english",
            max_features=100
        )

        matrix = vectorizer.fit_transform(
            texts
        )

        frequencies = (
            matrix.sum(axis=0)
            .A1
        )

        words = (
            vectorizer.get_feature_names_out()
        )

        result = sorted(
            zip(words, frequencies),
            key=lambda x: x[1],
            reverse=True
        )

        return result[:top_n]