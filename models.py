from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing_extensions import NotRequired, TypedDict


def replace_articles(_: list["ArticleModel"], new_articles: list["ArticleModel"]) -> list["ArticleModel"]:
    return new_articles


LayoutType = Literal["Hero", "Grid", "List"]
PhaseType = Literal["fetch_news", "curate_content", "determine_layout"]
StreamEventType = Literal["state_update", "error", "done"]


class ArticleModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    source_url: HttpUrl
    thumbnail_url: HttpUrl | None = None


class NewsStateModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    layout_type: LayoutType
    articles: list[ArticleModel]
    run_id: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    phase: PhaseType | None = None


class NewsGraphState(TypedDict, total=False):
    layout_type: LayoutType
    articles: Annotated[list[ArticleModel], replace_articles]
    run_id: NotRequired[str]
    updated_at: NotRequired[datetime]
    phase: NotRequired[PhaseType]


class ErrorPayloadModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    run_id: str
    details: list[dict] | None = None


class DonePayloadModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str


class StreamEventModel(BaseModel):
    """Runtime envelope for streamed NDJSON events."""

    model_config = ConfigDict(extra="forbid")

    type: StreamEventType
    payload: NewsStateModel | ErrorPayloadModel | DonePayloadModel

