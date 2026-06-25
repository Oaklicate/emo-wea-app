from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

# ---------------------------------------------------------------------------
# Column alias maps
# ---------------------------------------------------------------------------

DATE_ALIASES = {
    "date", "datetime", "timestamp", "created_at", "created",
    "published_at", "time", "publication_date",
}

TEXT_ALIASES = {
    "text", "message", "body", "comment", "content", "post", "message_text",
}

SENTIMENT_ALIASES = {"sentiment", "emotion", "label"}

SCORE_ALIASES = {"score", "sentiment_score", "emotion_score"}

# ---------------------------------------------------------------------------
# Target canonical column names
# ---------------------------------------------------------------------------

COL_DATE = "date"
COL_TEXT = "text"
COL_SENTIMENT = "sentiment"
COL_SCORE = "score"
COL_STATUS = "schema_status"

# ---------------------------------------------------------------------------
# Status values
# ---------------------------------------------------------------------------

STATUS_OK = "ok"
STATUS_MISSING_DATE = "missing_date"
STATUS_MISSING_TEXT = "missing_text"
STATUS_MISSING_SCORE = "missing_score"
STATUS_MISSING_SENTIMENT = "missing_sentiment"

# ---------------------------------------------------------------------------
# Fatal reason codes
# ---------------------------------------------------------------------------

FATAL_MISSING_TEXT = "missing_text_column"

# ---------------------------------------------------------------------------
# Warning messages
# ---------------------------------------------------------------------------

WARN_NO_DATE = "Дата отсутствует. Анализ динамики невозможен."
WARN_PARTIAL_DATE = "Часть строк не содержит даты. Они помечены как missing_date."
WARN_PARTIAL_TEXT = "Часть строк не содержит текста. Они помечены как missing_text."
WARN_NO_SENTIMENT = "Колонка тональности отсутствует. SentimentAgent выполнит анализ."
WARN_NO_SCORE = "Колонка оценки отсутствует. SentimentAgent выполнит расчёт."


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class AvailableFeatures:
    weather: bool = True
    forecast: bool = True
    spikes: bool = True
    narrative: bool = True
    visualization: bool = True
    report: bool = True


@dataclass
class SchemaResult:
    data: pd.DataFrame
    valid: bool
    fatal: bool
    warnings: list[str]
    missing_columns: list[str]
    skip_sentiment: bool
    available_features: AvailableFeatures
    reason: str = ""


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class SchemaAgent:

    def validate(self, df: pd.DataFrame) -> SchemaResult:
        df = df.copy()
        warnings: list[str] = []
        missing_columns: list[str] = []

        df = self._rename_columns(df)

        fatal, reason = self._check_fatal(df)
        if fatal:
            return self._fatal_result(df, reason, warnings, missing_columns)

        df, date_warnings, date_missing = self._process_date_column(df)
        warnings.extend(date_warnings)
        missing_columns.extend(date_missing)

        features = self._build_features(df)

        skip_sentiment = self._has_sentiment_and_score(df)

        if COL_SENTIMENT not in df.columns:
            warnings.append(WARN_NO_SENTIMENT)
            missing_columns.append(COL_SENTIMENT)

        if COL_SCORE not in df.columns:
            warnings.append(WARN_NO_SCORE)
            missing_columns.append(COL_SCORE)

        df = self._add_row_status(df)

        return SchemaResult(
            data=df,
            valid=True,
            fatal=False,
            warnings=warnings,
            missing_columns=missing_columns,
            skip_sentiment=skip_sentiment,
            available_features=features,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        alias_map = {
            **{alias: COL_DATE for alias in DATE_ALIASES},
            **{alias: COL_TEXT for alias in TEXT_ALIASES},
            **{alias: COL_SENTIMENT for alias in SENTIMENT_ALIASES},
            **{alias: COL_SCORE for alias in SCORE_ALIASES},
        }
        rename = {
            col: alias_map[col]
            for col in df.columns
            if col in alias_map
        }
        return df.rename(columns=rename)

    def _check_fatal(self, df: pd.DataFrame) -> tuple[bool, str]:
        if COL_TEXT not in df.columns:
            return True, FATAL_MISSING_TEXT
        return False, ""

    def _process_date_column(
        self,
        df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, list[str], list[str]]:
        warnings: list[str] = []
        missing: list[str] = []

        if COL_DATE not in df.columns:
            warnings.append(WARN_NO_DATE)
            missing.append(COL_DATE)
            return df, warnings, missing

        df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")

        partial_missing = df[COL_DATE].isna().any()
        if partial_missing:
            warnings.append(WARN_PARTIAL_DATE)

        return df, warnings, missing

    def _build_features(self, df: pd.DataFrame) -> AvailableFeatures:
        has_date = (
            COL_DATE in df.columns
            and df[COL_DATE].notna().any()
        )
        return AvailableFeatures(
            weather=has_date,
            forecast=has_date,
            spikes=has_date,
            narrative=True,
            visualization=True,
            report=True,
        )

    def _has_sentiment_and_score(self, df: pd.DataFrame) -> bool:
        return COL_SENTIMENT in df.columns and COL_SCORE in df.columns

    def _add_row_status(self, df: pd.DataFrame) -> pd.DataFrame:
        def _row_status(row: pd.Series) -> str:
            if COL_DATE in df.columns and pd.isna(row.get(COL_DATE)):
                return STATUS_MISSING_DATE
            text_val = row.get(COL_TEXT, None)
            if pd.isna(text_val) or str(text_val).strip() == "":
                return STATUS_MISSING_TEXT
            return STATUS_OK

        df[COL_STATUS] = df.apply(_row_status, axis=1)
        return df

    def _fatal_result(
        self,
        df: pd.DataFrame,
        reason: str,
        warnings: list[str],
        missing_columns: list[str],
    ) -> SchemaResult:
        missing_columns.append(COL_TEXT)
        features = AvailableFeatures(
            weather=False,
            forecast=False,
            spikes=False,
            narrative=False,
            visualization=False,
            report=False,
        )
        return SchemaResult(
            data=df,
            valid=False,
            fatal=True,
            warnings=warnings,
            missing_columns=missing_columns,
            skip_sentiment=False,
            available_features=features,
            reason=reason,
        )