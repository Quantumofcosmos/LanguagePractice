from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Token(StrictModel):
    text: str
    reading: Optional[str] = None
    kana: Optional[str] = None
    meaning: Optional[str] = None
    study: bool = False
    highlight: bool = False


class Language(StrictModel):
    tokens: list[Token] = Field(min_length=1)
    pattern: Optional[str] = None
    observation: Optional[str] = None

    @property
    def text(self) -> str:
        return "".join(token.text for token in self.tokens)

    @property
    def romanized(self) -> str:
        return " ".join(token.reading for token in self.tokens if token.reading)

    @property
    def study_tokens(self) -> list[Token]:
        # Explicit study choices only. This prevents WORDS from becoming
        # "the first three tokens that happen to have meanings".
        return [t for t in self.tokens if t.study][:3]


class Connection(StrictModel):
    title: str = ""
    text: str = ""

    def has_content(self) -> bool:
        return bool(self.title.strip() or self.text.strip())


class Project(StrictModel):
    title: str = "THE LITTLE PRINCE PROJECT"
    tagline: str = "one book · three languages · one sentence at a time"


class LanguageLabels(StrictModel):
    english: str = "ENGLISH"
    chinese: str = "中文"
    japanese: str = "日本語"
    german: str = "DEUTSCH"


class Post(StrictModel):
    number: int = Field(ge=1)
    chapter: int = Field(ge=1)
    sentence: int = Field(ge=1)
    english: Language
    chinese: Language
    japanese: Language
    german: Language
    connection: Optional[Connection] = None
    field_note: Optional[str] = None
    project: Project = Field(default_factory=Project)
    labels: LanguageLabels = Field(default_factory=LanguageLabels)

    @model_validator(mode="after")
    def require_text(self):
        for name in ("english", "chinese", "japanese", "german"):
            lang = getattr(self, name)
            if not any(t.text.strip() for t in lang.tokens):
                raise ValueError(f"{name}.tokens must contain text")
        return self
