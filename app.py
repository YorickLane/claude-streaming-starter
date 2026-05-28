"""FastAPI SSE endpoint streaming Claude responses to the browser.

Run locally:
    pip install -r requirements.txt
    cp .env.example .env  # add ANTHROPIC_API_KEY
    uvicorn app:app --reload
Then open http://localhost:8000/

Endpoints:
    GET /         -> minimal chat UI
    GET /chat?msg=... -> SSE stream of text deltas + final cost summary

Production patterns demonstrated:
    - True streaming via messages.stream() (token-by-token)
    - Server-Sent Events (works with native EventSource on any frontend)
    - Prompt caching configured on the system prompt
    - Per-request input/output token + cost tracking
    - Frontend cancellation detection (closes Anthropic stream on disconnect)
    - Automatic retry on 429 / 5xx (anthropic SDK default max_retries=2)
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse

load_dotenv()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOG = logging.getLogger("starter")

from claude_client import MODEL, stream_chat  # noqa: E402 (after load_dotenv)
from cost import calc_cost  # noqa: E402

app = FastAPI(title="Claude Streaming Starter")

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/chat")
async def chat(request: Request, msg: str) -> StreamingResponse:
    """SSE endpoint. EventSource on the browser side handles reconnection."""

    async def event_stream():
        # Demo: no persistent history. Real app would load + persist by session/user.
        history: list[dict[str, str]] = []
        final = None

        try:
            async for text_delta, maybe_final in stream_chat(msg, history):
                if await request.is_disconnected():
                    LOG.info("client disconnected mid-stream; cancelling Anthropic call")
                    return
                if maybe_final is not None:
                    final = maybe_final
                if text_delta:
                    yield f"data: {json.dumps({'type': 'delta', 'text': text_delta})}\n\n"
        except Exception as e:
            LOG.exception("stream error: %s", e)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        if final is not None:
            cost = calc_cost(MODEL, final.usage)
            LOG.info(
                "request done: in=%d cached_read=%d cached_write=%d out=%d cost=$%.6f",
                cost["uncached_input_tokens"],
                cost["cache_read_tokens"],
                cost["cache_write_tokens"],
                cost["output_tokens"],
                cost["cost_usd"],
            )
            yield f"data: {json.dumps({'type': 'done', 'cost': cost})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "model": MODEL}
