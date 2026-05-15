from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.schemas import StreamRequest
from api.streaming import event_stream

news_router = APIRouter()


@news_router.post("/api/news/stream")
async def stream_news(request: StreamRequest) -> StreamingResponse:
    run_id = request.run_id or str(uuid4())
    return StreamingResponse(
        event_stream(run_id),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache"},
    )

