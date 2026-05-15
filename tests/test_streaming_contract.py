import asyncio
import json

from api.streaming import event_stream
from graph import fetch_tavily_news


async def _collect_events(run_id: str) -> list[dict]:
    events: list[dict] = []
    async for chunk in event_stream(run_id):
        events.append(json.loads(chunk))
    return events


def test_event_stream_emits_state_updates_and_done(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    events = asyncio.run(_collect_events("test_run"))

    assert len(events) >= 2
    assert events[-1]["type"] == "done"
    assert events[-1]["payload"]["run_id"] == "test_run"

    state_updates = [event for event in events if event["type"] == "state_update"]
    assert len(state_updates) >= 1
    assert state_updates[-1]["payload"]["layout_type"] in {"Hero", "Grid", "List"}
    assert isinstance(state_updates[-1]["payload"]["articles"], list)


def test_fetch_tavily_news_uses_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    articles = fetch_tavily_news()

    assert articles
    assert all(article.title for article in articles)
    assert all(article.source_url for article in articles)
