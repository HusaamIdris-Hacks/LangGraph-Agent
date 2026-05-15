# LangGraph Agent

State-driven tech news app built with **LangGraph**, **FastAPI**, **Gemini**, and **Next.js**.

## Stack

- **Backend:** LangGraph + FastAPI
- **Frontend:** Next.js App Router + React 19
- **Contract validation:** Pydantic (Python) + Zod (TypeScript)

## Backend Overview

- Graph workflow: `fetch_news -> curate_content -> determine_layout`
- Graph state schema:
  - `layout_type`: `"Hero" | "Grid" | "List"`
  - `articles`: list of `{ title, summary, source_url, thumbnail_url? }`
  - metadata: `run_id`, `updated_at`, `phase`
- Streaming endpoint: `POST /api/news/stream`
- Stream format: NDJSON with event envelopes:
  - `state_update`
  - `error`
  - `done`

Key files:

- `models.py` - typed state and Pydantic contracts
- `graph.py` - StateGraph nodes, Gemini news agent, Tavily tool, and compiled graph
- `api/streaming.py` - `astream_events` bridge and stream validation
- `api/routes.py` - FastAPI endpoint
- `contracts/news_state.schema.json` - exported JSON schema artifact

## Environment

Create a local `.env` file in the repository root:

```env
GOOGLE_API_KEY=your_google_ai_studio_api_key
TAVILY_API_KEY=your_tavily_api_key
# Optional; defaults to gemini-2.5-flash
GEMINI_MODEL=gemini-2.5-flash
```

`fetch_news` uses Gemini as a tech-news agent and exposes Tavily search as its tool. Gemini selects the query and returns structured articles that match the renderer contract. If `GOOGLE_API_KEY` is missing, the backend uses Tavily directly. If `TAVILY_API_KEY` is missing or Tavily is unavailable, the backend falls back to sample articles so the UI remains usable during local development.

## Frontend Overview

The `frontend/` app includes:

- `src/lib/news-schema.ts` - Zod contract for backend stream events
- `src/lib/useNewsStream.ts` - NDJSON streaming hook
- `src/components/layouts/*` - `Hero`, `Grid`, and `List` renderers
- `src/components/NewsRenderer.tsx` - layout discriminator renderer
- `src/app/page.tsx` - App Router page consuming stream updates in real time

## Run Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then stream:

```bash
curl -N -X POST http://localhost:8000/api/news/stream -H "Content-Type: application/json" -d "{}"
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_NEWS_STREAM_URL` if your API is not at `http://localhost:8000/api/news/stream`.

## Contract Validation

Python tests:

```bash
PYTHONPATH=. pytest tests
```

Frontend schema tests:

```bash
cd frontend
npm run test:schema
```

Regenerate schema artifact:

```bash
python3 scripts/export_schema.py
```
