from pydantic import BaseModel, ConfigDict


class StreamRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str | None = None
