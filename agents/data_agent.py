import json
import re
from io import StringIO

import pandas as pd
import toml


SUPPORTED_EXTENSIONS = (".csv", ".json", ".toml")

DEFAULT_ENCODING = "utf-8"
FALLBACK_ENCODINGS = (
    "utf-8",
    "utf-8-sig",
    "cp1251",
    "windows-1251",
    "latin1",
)

CSV_SEPARATORS = [",", ";", "\t", "|"]

DATE_ALIASES = [
    "date",
    "datetime",
    "created_at",
    "created",
    "publish_date",
    "published_at",
    "publication_date",
    "timestamp",
    "time",
]

TEXT_ALIASES = [
    "text",
    "body",
    "message",
    "content",
    "comment",
    "post",
    "caption",
]

LIKES_ALIASES = [
    "likes",
    "like",
    "likes_count",
]

COMMENTS_ALIASES = [
    "comments",
    "comments_count",
]

REPOSTS_ALIASES = [
    "reposts",
    "shares",
    "share_count",
]

VIEWS_ALIASES = [
    "views",
    "views_count",
]

ERR_EMPTY = "Файл не содержит данных."
ERR_UNSUPPORTED = "Формат файла не поддерживается."


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\w]", "_", regex=True)
    )

    return df


def decode_bytes(raw: bytes) -> str:

    for enc in FALLBACK_ENCODINGS:
        try:
            return raw.decode(enc)
        except Exception:
            pass

    return raw.decode(DEFAULT_ENCODING, errors="ignore")


def read_csv(uploaded_file):

    raw = uploaded_file.read()

    text = decode_bytes(raw)

    for sep in CSV_SEPARATORS:

        try:

            df = pd.read_csv(
                StringIO(text),
                sep=sep,
                engine="python",
            )

            if len(df.columns) > 1:
                return df

        except Exception:
            pass

    return pd.read_csv(StringIO(text))


def read_json(uploaded_file):

    data = json.load(uploaded_file)

    # -------------------------
    # Если сразу список
    # -------------------------

    if isinstance(data, list):
        return pd.DataFrame(data)

    # -------------------------
    # Если словарь
    # -------------------------

    if isinstance(data, dict):

        # Самые популярные структуры

        candidates = [
            "records",
            "items",
            "posts",
            "messages",
            "wall",
            "comments",
            "data",
            "result",
            "response",
        ]

        for key in candidates:

            if key not in data:
                continue

            value = data[key]

            if isinstance(value, list):
                return pd.DataFrame(value)

            # VK API
            if isinstance(value, dict):

                if "items" in value:

                    if isinstance(value["items"], list):
                        return pd.DataFrame(value["items"])

                for sub in value.values():

                    if isinstance(sub, list):
                        return pd.DataFrame(sub)

        # Любой первый найденный список

        for value in data.values():

            if isinstance(value, list):
                return pd.DataFrame(value)

        # Вложенный словарь

        for value in data.values():

            if isinstance(value, dict):

                for sub in value.values():

                    if isinstance(sub, list):
                        return pd.DataFrame(sub)

        # Последний вариант

        return pd.json_normalize(data)

    raise ValueError("Не удалось определить структуру JSON.")


def read_toml(uploaded_file):

    raw = uploaded_file.read()

    text = decode_bytes(raw)

    data = toml.loads(text)

    if "records" in data:
        return pd.DataFrame(data["records"])

    for value in data.values():
        if isinstance(value, list):
            return pd.DataFrame(value)

    raise ValueError("Не удалось определить структуру TOML.")


READERS = {
    ".csv": read_csv,
    ".json": read_json,
    ".toml": read_toml,
}


def find_column(df, aliases):

    for alias in aliases:

        if alias in df.columns:
            return alias

    for column in df.columns:

        for alias in aliases:

            if alias in column:
                return column

    return None


def to_datetime(series):

    return pd.to_datetime(
        series,
        errors="coerce",
    )


def to_numeric(series):

    return (
        series.astype(str)
        .str.replace(",", ".", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0]
        .pipe(pd.to_numeric, errors="coerce")
    )

class DataAgent:

    @staticmethod
    def load_file(uploaded_file) -> pd.DataFrame:

        ext = DataAgent._extension(uploaded_file.name)

        if ext not in READERS:
            raise ValueError(ERR_UNSUPPORTED)

        df = READERS[ext](uploaded_file)

        if df.empty:
            raise ValueError(ERR_EMPTY)

        df = normalize_columns(df)

        df = DataAgent._normalize_schema(df)
        df = DataAgent._repair_dataframe(df)    
        df = DataAgent._clean_dataframe(df)

        df = df.reset_index(drop=True)

        DataAgent.profile = profile_dataframe(df)
        DataAgent.warnings = validate_dataframe(df)

        return df

    @staticmethod
    def _extension(filename):

        filename = filename.lower()

        for ext in SUPPORTED_EXTENSIONS:
            if filename.endswith(ext):
                return ext

        return ""

    @staticmethod
    def _normalize_schema(df):

        aliases = {
            "date": DATE_ALIASES,
            "text": TEXT_ALIASES,
            "likes": LIKES_ALIASES,
            "comments": COMMENTS_ALIASES,
            "views": VIEWS_ALIASES,
            "reposts": REPOSTS_ALIASES,
        }

        rename = {}

        for target, alias_list in aliases.items():

            column = find_column(df, alias_list)

            if column:
                rename[column] = target

        df = df.rename(columns=rename)

        # -----------------------
        # VK EXPORT
        # -----------------------

        if "text" not in df.columns:

            for col in df.columns:

                if "text" in col.lower():
                    df = df.rename(columns={col: "text"})
                    break

        if "date" not in df.columns:

            for col in df.columns:

                low = col.lower()

                if (
                    "date" in low
                    or "time" in low
                    or "created" in low
                ):
                    df = df.rename(columns={col: "date"})
                    break

        return df     

    @staticmethod
    def _repair_dataframe(df):

        # Если вообще нет текста —
        # пытаемся найти самую длинную строковую колонку

        if "text" not in df.columns:

            text_candidates = []

            for col in df.columns:

                if df[col].dtype == object:

                    avg = (
                        df[col]
                        .fillna("")
                        .astype(str)
                        .str.len()
                        .mean()
                    )

                    text_candidates.append((avg, col))

            if text_candidates:

                text_candidates.sort(reverse=True)

                df = df.rename(
                    columns={
                        text_candidates[0][1]: "text"
                    }
                )

        return df
    @staticmethod
    def _clean_dataframe(df):

        # ---------- TEXT ----------

        if "text" not in df.columns:
            df["text"] = ""

        df["text"] = (
            df["text"]
            .fillna("")
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # ---------- DATE ----------

        if "date" not in df.columns:
            df["date"] = pd.NaT
        else:
            df["date"] = to_datetime(df["date"])

        # ---------- NUMBERS ----------

        for col in ["likes", "comments", "views", "reposts"]:

            if col not in df.columns:
                df[col] = 0

            df[col] = to_numeric(df[col]).fillna(0)

        # ---------- REMOVE DUPLICATES ----------

        df = df.drop_duplicates()

        # ---------- REMOVE EMPTY ----------

        if "text" in df.columns:

            df = df[
                (df["text"].astype(str).str.strip() != "")
                |
                (df["date"].notna())
            ]

        return df.reset_index(drop=True)
def profile_dataframe(df):

    profile = {}

    profile["rows"] = len(df)

    profile["columns"] = len(df.columns)

    profile["missing"] = (
        df.isna()
        .sum()
        .to_dict()
    )

    profile["duplicates"] = int(df.duplicated().sum())

    profile["columns_list"] = list(df.columns)

    return profile


def validate_dataframe(df):

    warnings = []

    if len(df) == 0:
        warnings.append("Файл не содержит валидных записей.")

    if "text" not in df.columns:
        warnings.append("Не найден текст сообщений.")

    if "date" not in df.columns:
        warnings.append("Не найдена дата сообщений.")

    if df.duplicated().any():
        warnings.append("Обнаружены дубликаты.")

    return warnings