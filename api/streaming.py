from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, AsyncIterator

from pydantic import ValidationError

from graph import news_graph
from models import (
    DonePayloadModel,
    ErrorPayloadModel,
    NewsStateModel,
    StreamEventModel,
)

GRAPH_NODE_NAMES = {"fetch_news", "curate_content", "determine_layout"}


def to_ndjson(payload: dict[str, Any]) -> str:
    return json.dumps(payload, default=str) + "\n"


def build_initial_snapshot(run_id: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "layout_type": "List",
        "articles": [],
        "updated_at": datetime.now(UTC),
        "phase": "fetch_news",
    }


def validate_news_state(snapshot: dict[str, Any]) -> dict[str, Any]:
    return NewsStateModel.model_validate(snapshot).model_dump(mode="json")


def build_stream_event(
    event_type: str,
    payload: dict[str, Any],
) -> str:
    stream_event = StreamEventModel.model_validate({"type": event_type, "payload": payload})
    return to_ndjson(stream_event.model_dump(mode="json"))


async def event_stream(run_id: str) -> AsyncIterator[str]:
    state_snapshot = build_initial_snapshot(run_id)

    try:
        async for event in news_graph.astream_events({"run_id": run_id}, version="v2"):
            if event.get("event") != "on_chain_end":
                continue

            if event.get("name") not in GRAPH_NODE_NAMES:
                continue

            output = event.get("data", {}).get("output")
            if isinstance(output, dict):
                state_snapshot.update(output)

            payload = validate_news_state(state_snapshot)
            yield build_stream_event("state_update", payload)

        done_payload = DonePayloadModel(run_id=run_id).model_dump(mode="json")
        yield build_stream_event("done", done_payload)
    except ValidationError as exc:
        error_payload = ErrorPayloadModel(
            message="State validation failed",
            details=exc.errors(),
            run_id=run_id,
        ).model_dump(mode="json")
        done_payload = DonePayloadModel(run_id=run_id).model_dump(mode="json")
        yield build_stream_event("error", error_payload)
        yield build_stream_event("done", done_payload)
    except Exception:
        error_payload = ErrorPayloadModel(
            message="Stream failed",
            run_id=run_id,
        ).model_dump(mode="json")
        done_payload = DonePayloadModel(run_id=run_id).model_dump(mode="json")
        yield build_stream_event("error", error_payload)
        yield build_stream_event("done", done_payload)
