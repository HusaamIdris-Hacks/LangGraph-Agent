import json

from fastapi.testclient import TestClient

from main import app


def test_stream_endpoint_emits_done_event(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    client = TestClient(app)
    response = client.post("/api/news/stream", json={})

    assert response.status_code == 200

    events: list[dict] = []
    for line in response.iter_lines():
        if not line:
            continue
        events.append(json.loads(line))

    assert len(events) >= 2
    assert events[-1]["type"] == "done"
