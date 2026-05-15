from datetime import UTC, datetime

from pydantic import ValidationError

from models import ArticleModel, NewsStateModel


def test_news_state_model_accepts_valid_payload() -> None:
    payload = {
        "layout_type": "Grid",
        "articles": [
            ArticleModel(
                title="LangGraph workflows at scale",
                summary="State-first orchestration improves reliability for AI apps.",
                source_url="https://example.com/langgraph-scale",
            ).model_dump(mode="json")
        ],
        "run_id": "run_123",
        "updated_at": datetime.now(UTC).isoformat(),
        "phase": "curate_content",
    }

    model = NewsStateModel.model_validate(payload)
    assert model.layout_type == "Grid"
    assert len(model.articles) == 1
    assert str(model.articles[0].source_url) == "https://example.com/langgraph-scale"


def test_article_model_accepts_optional_thumbnail() -> None:
    article = ArticleModel(
        title="Gemini launches new model",
        summary="A faster model targets agent workloads.",
        source_url="https://example.com/gemini-launch",
        thumbnail_url="https://example.com/thumb.jpg",
    )

    assert article.thumbnail_url is not None
    assert str(article.thumbnail_url) == "https://example.com/thumb.jpg"


def test_news_state_model_rejects_invalid_layout() -> None:
    bad_payload = {
        "layout_type": "Masonry",
        "articles": [],
    }

    try:
        NewsStateModel.model_validate(bad_payload)
        assert False, "Expected validation failure"
    except ValidationError as exc:
        assert "layout_type" in str(exc)
