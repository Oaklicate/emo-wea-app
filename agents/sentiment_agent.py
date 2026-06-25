import pandas as pd
from transformers import pipeline

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
MAX_TEXT_LENGTH = 512
DEFAULT_SENTIMENT = "neutral"
DEFAULT_SCORE = 0

LABEL_TO_SCORE = {
    "positive": 1,
    "negative": -1,
    "neutral": 0,
}


class SentimentAgent:

    def __init__(self):
        self._classifier = None

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        classifier = self._get_classifier()
        texts = df["text"].fillna("").astype(str).tolist()
        sentiments, scores = zip(
            *(self._classify(classifier, t) for t in texts)
        )
        df = df.copy()
        df["sentiment"] = list(sentiments)
        df["score"] = list(scores)
        return df

    def _get_classifier(self):
        if self._classifier is None:
            self._classifier = pipeline(
                "sentiment-analysis",
                model=MODEL_NAME,
            )
        return self._classifier

    def _classify(self, classifier, text: str):
        text = text.strip()
        if not text:
            return DEFAULT_SENTIMENT, DEFAULT_SCORE
        try:
            result = classifier(text[:MAX_TEXT_LENGTH])[0]
            label = result["label"]
            score = LABEL_TO_SCORE.get(label, DEFAULT_SCORE)
            return label, score
        except Exception:
            return DEFAULT_SENTIMENT, DEFAULT_SCORE
