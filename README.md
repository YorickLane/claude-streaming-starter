# Claude Streaming Starter

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Built with Anthropic](https://img.shields.io/badge/built%20with-Claude%20API-DA7756)](https://www.anthropic.com)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org)
[![Stars](https://img.shields.io/github/stars/YorickLane/claude-streaming-starter?style=social)](https://github.com/YorickLane/claude-streaming-starter)

A minimal, production-shaped FastAPI endpoint that streams Claude API responses to the browser via Server-Sent Events (SSE). ~180 LoC, no framework bloat.

```bash
# 30-second try (after adding your ANTHROPIC_API_KEY to .env):
docker build -t claude-streaming-starter . && \
  docker run -p 8000:8000 --env-file .env claude-streaming-starter
# → open http://localhost:8000
```

Or [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YorickLane/claude-streaming-starter)

## Why this exists

Most "Claude streaming" tutorials online either:

- Use blocking calls (`messages.create()` not `messages.stream()`) — defeats the point
- Use Vercel AI SDK or langchain wrappers — too much magic, too much dep weight
- Skip the **production stuff**: token cost tracking, retry on transient errors, frontend cancellation handling, prompt caching

This template has all four. ~180 LoC. Drop into any FastAPI app.

## Features

- ✅ True streaming via `client.messages.stream()` (token-by-token to browser)
- ✅ Server-Sent Events response (works with `EventSource` on any frontend)
- ✅ Prompt caching enabled on the system prompt (90% cost cut on repeated calls)
- ✅ Per-request input/output token tracking + cost calculation
- ✅ Frontend cancellation detection (closes Anthropic stream on client disconnect — no zombie token spend)
- ✅ SDK built-in retry on 429 / 5xx (max_retries=2 default; override per-call via `.with_options(max_retries=N)`)
- ✅ Type hints throughout, mypy/pyright clean

## Quick start

```bash
git clone https://github.com/YorickLane/claude-streaming-starter.git
cd claude-streaming-starter
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
$EDITOR .env  # add ANTHROPIC_API_KEY

uvicorn app:app --reload
# open http://localhost:8000 — chat UI included
```

## Architecture

```
Browser (EventSource)
    │
    │  GET /chat?msg=Hello&conv_id=abc
    ▼
FastAPI endpoint  ──────►  Anthropic API (streaming)
    │                            │
    │  SSE chunks               │  message_start
    │  ◄────────────────────    │  content_block_delta
    │                            │  content_block_delta
    │  Cost tracker             │  ...
    │  ◄────────────────────    │  message_stop
    │                            │
    │  Disconnect detection    │
    └──► cancel stream ────────►  (no zombie spend)
```

## Files

| File | Purpose |
|---|---|
| `app.py` | FastAPI app + SSE endpoint (~120 LoC) |
| `claude_client.py` | Thin wrapper around Anthropic SDK with caching + retry (~40 LoC) |
| `cost.py` | Per-model token-cost calculator (~15 LoC) |
| `static/index.html` | Minimal chat UI using `EventSource` |
| `requirements.txt` | `anthropic`, `fastapi`, `uvicorn` |

## Cost tracking output (sample)

```
2026-05-26 19:42:31 INFO request_id=abc cached_input_tokens=4521 fresh_input_tokens=87
                         output_tokens=234 cost_usd=0.00284
```

## Why this template wins on Fiverr / Upwork

Most freelancers ship Claude integrations that work *demos* but break in production. This template encodes the production patterns I've shipped over 18 months of daily Claude API work:

- Prompt caching is **non-default in the SDK** — you have to configure it explicitly. Most freelancers don't.
- Frontend cancellation → backend stream cancellation is **never** in tutorials. Without it, a user closing their tab still costs you tokens for the next 30 seconds.
- Retry on 429: the SDK has built-in retry; this template makes the per-call override pattern explicit so you can tune backoff to your workload.

## License

MIT. Use freely.

## Author

Boxiang Z. — [Fiverr profile](https://www.fiverr.com/boxiangzhao245)

Available for Claude API integration work via Fiverr. Async-only delivery.
