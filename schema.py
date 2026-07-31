from __future__ import annotations
from typing import Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

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
    def text(self): return "".join(t.text for t in self.tokens)
    @property
    def romanized(self): return " ".join(t.reading for t in self.tokens if t.reading)
    @property
    def study_tokens(self): return [t for t in self.tokens if t.study][:3]

class Connection(StrictModel):
    title: str = ""
    text: str = ""
    def has_content(self): return bool(self.title.strip() or self.text.strip())

class Project(StrictModel):
    title: str = "LANGUAGE PRACTICE"
    tagline: str = "three languages · one journey"

class LanguageLabels(StrictModel):
    english: str = "ENGLISH"
    chinese: str = "中文"
    japanese: str = "日本語"
    german: str = "DEUTSCH"

class SentencePost(StrictModel):
    type: Literal["sentence"] = "sentence"
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
        for name in ("english","chinese","japanese","german"):
            if not any(t.text.strip() for t in getattr(self,name).tokens):
                raise ValueError(f"{name}.tokens must contain text")
        return self

class VocabWord(StrictModel):
    text: str
    reading: Optional[str] = None
    kana: Optional[str] = None
    note: Optional[str] = None

class VocabConcept(StrictModel):
    english: str
    chinese: VocabWord
    japanese: VocabWord
    german: VocabWord

class UsageExample(StrictModel):
    english: str
    chinese: Optional[str] = None
    chinese_reading: Optional[str] = None
    japanese: Optional[str] = None
    japanese_kana: Optional[str] = None
    japanese_reading: Optional[str] = None
    german: Optional[str] = None

class VocabularyPost(StrictModel):
    type: Literal["vocabulary"]
    number: int = Field(ge=1)
    title: str
    subtitle: Optional[str] = None
    concepts: list[VocabConcept] = Field(min_length=3, max_length=6)
    usage: list[UsageExample] = Field(default_factory=list, max_length=5)
    note: Optional[str] = None
    project: Project = Field(default_factory=Project)
    labels: LanguageLabels = Field(default_factory=LanguageLabels)

Post = Union[SentencePost, VocabularyPost]
PostAdapter = TypeAdapter(Post)
