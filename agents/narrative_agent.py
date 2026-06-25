import re

from sklearn.feature_extraction.text import CountVectorizer

STOP_WORDS = {
    "и", "в", "во", "на", "под", "над", "из", "за", "по", "до", "от", "об",
    "о", "у", "к", "с", "со", "не", "но", "а", "да", "ни", "то", "же",
    "ли", "бы", "ну", "вот", "как", "что", "это", "так", "все", "был", "была",
    "были", "есть", "быть", "уже", "еще", "ещё", "для", "при", "если", "когда",
    "или", "её", "его", "их", "он", "она", "они", "мы", "вы", "я", "ты",
    "мне", "меня", "тебя", "тебе", "нас", "вас", "им", "ему", "ей", "нет",
    "те", "тот", "та", "тем", "там", "тут", "здесь", "сейчас", "очень",
    "ведь", "даже", "именно", "хотя", "чтобы", "потому", "поэтому",
    "между", "через", "после", "перед", "всё", "этот", "эта", "эти",
    "каждый", "свой", "своя", "свои", "свое", "один", "два", "три", "себя",
    "которые", "который", "которая", "которое", "где", "куда", "откуда",
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "for", "with", "on", "in", "at", "by", "from", "as", "into",
    "that", "this", "it", "its", "he", "she", "they", "we", "you", "i",
    "and", "or", "but", "not", "no", "so", "if", "do", "did", "does",
    "have", "has", "had", "will", "would", "could", "should", "can", "may",
    "just", "also", "more", "than", "then", "when", "there", "their", "them",
    "what", "which", "who", "how", "all", "any", "my", "your", "our",
}

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE,
)
_DIGITS_RE = re.compile(r"\d+")
_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACES_RE = re.compile(r"\s+")
_SHORT_WORD_RE = re.compile(r"\b\w{1,2}\b")


class NarrativeAgent:

    def get_topics(self, df, top_n=10):
        corpus = self._prepare_corpus(df)
        if not corpus:
            return []
        vectorizer = self._build_vectorizer()
        try:
            matrix = vectorizer.fit_transform(corpus)
        except ValueError:
            return []
        frequencies = matrix.sum(axis=0).A1
        words = vectorizer.get_feature_names_out()
        result = sorted(zip(words, frequencies), key=lambda x: x[1], reverse=True)
        return result[:top_n]

    def _prepare_corpus(self, df):
        texts = df["text"].dropna().astype(str).tolist()
        cleaned = [self._clean_text(t) for t in texts]
        return [t for t in cleaned if t.strip()]

    def _clean_text(self, text):
        text = text.lower()
        text = _URL_RE.sub(" ", text)
        text = _EMAIL_RE.sub(" ", text)
        text = _EMOJI_RE.sub(" ", text)
        text = _DIGITS_RE.sub(" ", text)
        text = _PUNCT_RE.sub(" ", text)
        text = _SHORT_WORD_RE.sub(" ", text)
        text = _SPACES_RE.sub(" ", text)
        return text.strip()

    def _build_vectorizer(self):
        return CountVectorizer(
            stop_words=list(STOP_WORDS),
            max_features=200,
            ngram_range=(1, 2),
            min_df=2,
            token_pattern=r"[а-яёa-z]{3,}",
        )