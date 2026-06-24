from transformers import pipeline
import pandas as pd


class SentimentAgent:

    def __init__(self):

        self.classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )

    def analyze(self, df):

        sentiments = []
        scores = []

        texts = df["text"].astype(str).tolist()

        for text in texts:

            try:

                result = self.classifier(text[:512])[0]

                label = result["label"]

                if label == "positive":

                    score = 1

                elif label == "negative":

                    score = -1

                else:

                    score = 0

                sentiments.append(label)
                scores.append(score)

            except Exception:

                sentiments.append("neutral")
                scores.append(0)

        df["sentiment"] = sentiments
        df["score"] = scores

        return df