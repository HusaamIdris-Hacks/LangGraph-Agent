from __future__ import annotations

import json
from datetime import UTC, datetime
import os
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
import httpx
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from models import ArticleModel, LayoutType, NewsGraphState

load_dotenv()

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
DEFAULT_NEWS_QUERY = "latest technology news AI startups software cybersecurity today"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _fallback_articles() -> list[ArticleModel]:
    """Local fallback keeps the UI usable when Tavily is not configured."""
    return [
        ArticleModel(
            title="LangGraph ships stronger state orchestration patterns",
            summary="Teams can now model deterministic AI workflows with explicit state transitions.",
            source_url="https://example.com/langgraph-state-orchestration",
        ),
        ArticleModel(
            title="LangSmith extends run tracing and eval analysis",
            summary="Expanded observability helps debug quality regressions earlier in development.",
            source_url="https://example.com/langsmith-tracing-evals",
        ),
        ArticleModel(
            title="LangChain emphasizes modern runnable-based composition",
            summary="Runnable pipelines improve composability compared with older legacy chain styles.",
            source_url="https://example.com/langchain-runnables",
        ),
        ArticleModel(
            title="Production AI reliability patterns for 2026",
            summary="A practical guide for retries, fallbacks, and robust telemetry in LLM apps.",
            source_url="https://example.com/ai-reliability-patterns",
        ),
    ]


def _parse_optional_http_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned.startswith(("http://", "https://")):
        return None
    return cleaned


def _extract_thumbnail_from_tavily_result(result: dict[str, Any]) -> str | None:
    for key in ("image", "image_url", "thumbnail", "thumbnail_url"):
        thumbnail = _parse_optional_http_url(result.get(key))
        if thumbnail:
            return thumbnail
    return None


def _normalize_tavily_result(result: dict[str, Any]) -> ArticleModel | None:
    title = str(result.get("title") or "").strip()
    source_url = str(result.get("url") or "").strip()
    summary = str(result.get("content") or result.get("snippet") or "").strip()
    thumbnail_url = _extract_thumbnail_from_tavily_result(result)

    if not title or not source_url or not summary:
        return None

    try:
        return ArticleModel(
            title=title,
            summary=summary,
            source_url=source_url,
            thumbnail_url=thumbnail_url,
        )
    except ValueError:
        return None


def fetch_tavily_news(query: str = DEFAULT_NEWS_QUERY, max_results: int = 12) -> list[ArticleModel]:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return _fallback_articles()

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "topic": "news",
        "days": 7,
        "max_results": min(max_results, 12),
        "include_answer": False,
        "include_raw_content": False,
        "include_images": True,
    }

    try:
        response = httpx.post(TAVILY_SEARCH_URL, json=payload, timeout=20)
        response.raise_for_status()
    except httpx.HTTPError:
        return _fallback_articles()

    data = response.json()
    fallback_images = [
        url
        for item in data.get("images", [])
        if (url := _parse_optional_http_url(item)) is not None
    ]
    articles: list[ArticleModel] = []
    for index, result in enumerate(data.get("results", [])):
        if not isinstance(result, dict):
            continue
        if not _extract_thumbnail_from_tavily_result(result) and index < len(fallback_images):
            result = {**result, "image": fallback_images[index]}
        article = _normalize_tavily_result(result)
        if article is not None:
            articles.append(article)

    return articles or _fallback_articles()


class AgentNewsResult(BaseModel):
    articles: list[ArticleModel] = Field(min_length=1, max_length=12)

def _article_to_tool_payload(article: ArticleModel) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": article.title,
        "summary": article.summary,
        "source_url": str(article.source_url),
    }
    if article.thumbnail_url is not None:
        payload["thumbnail_url"] = str(article.thumbnail_url)
    return payload


def fetch_gemini_agent_news() -> list[ArticleModel]:
    if not os.environ.get("GOOGLE_API_KEY"):
        return fetch_tavily_news()

    if not os.environ.get("TAVILY_API_KEY"):
        return _fallback_articles()

    try:
        from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
        from langchain_core.tools import tool
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        return fetch_tavily_news()

    @tool
    def search_latest_tech_news(query: str, max_results: int = 20) -> list[dict[str, str]]:
        """Search Tavily for recent technology news and return normalized article candidates."""
        articles = fetch_tavily_news(query=query, max_results=max_results)
        return [_article_to_tool_payload(article) for article in articles]

    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
    tool_enabled_llm = llm.bind_tools([search_latest_tech_news])

    system_prompt = (
        "You are a tech news editor. Use the search_latest_tech_news tool to find current, real tech news. "
        "Prefer AI, software, startups, developer tools, cybersecurity, chips, and cloud infrastructure. "
        "Do not invent titles, summaries, URLs, or thumbnail_url values."
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                "Find the latest important technology news for a concise daily dashboard. "
                "Call the search tool with a focused query and return only articles backed by tool results."
            )
        ),
    ]

    try:
        tool_request = tool_enabled_llm.invoke(messages)
        messages.append(tool_request)

        candidate_payloads: list[dict[str, str]] = []
        for tool_call in getattr(tool_request, "tool_calls", [])[:3]:
            if tool_call.get("name") != search_latest_tech_news.name:
                continue

            tool_result = search_latest_tech_news.invoke(tool_call.get("args", {}))
            if isinstance(tool_result, list):
                candidate_payloads.extend(tool_result)

            messages.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

        if not candidate_payloads:
            candidate_payloads = [_article_to_tool_payload(article) for article in fetch_tavily_news()]

        structured_llm = llm.with_structured_output(AgentNewsResult)
        selection = structured_llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Select the strongest current tech news articles from the provided Tavily candidates. "
                        "Return valid structured data only. Keep summaries concise. Preserve each source_url "
                        "and thumbnail_url exactly when provided in candidates; omit thumbnail_url if absent."
                    )
                ),
                HumanMessage(content=json.dumps({"candidates": candidate_payloads})),
            ]
        )
    except Exception:
        return fetch_tavily_news()

    if isinstance(selection, AgentNewsResult):
        return selection.articles

    try:
        return AgentNewsResult.model_validate(selection).articles
    except ValueError:
        return fetch_tavily_news()


def fetch_news(state: NewsGraphState) -> NewsGraphState:
    """Fetch articles through the Gemini agent and normalize them into ArticleModel objects."""
    articles = state.get("articles")
    if not articles:
        articles = fetch_gemini_agent_news()

    return {
        "run_id": state.get("run_id", str(uuid4())),
        "layout_type": state.get("layout_type", "List"),
        "articles": articles,
        "phase": "fetch_news",
        "updated_at": _utc_now(),  
    }


def curate_content(state: NewsGraphState) -> NewsGraphState:
    """Deduplicate, rank, and trim content for downstream layout decisions."""
    deduped: dict[str, ArticleModel] = {}
    for article in state.get("articles", []):
        deduped[str(article.source_url)] = article

    ranked = sorted(
        deduped.values(),
        key=lambda item: (len(item.title), item.title),
        reverse=True,
    )
    curated = ranked[:12]

    return {
        "layout_type": state.get("layout_type", "List"),
        "articles": curated,
        "phase": "curate_content",
        "updated_at": _utc_now(),
    }


def determine_layout(state: NewsGraphState) -> NewsGraphState:
    """Pick Hero/Grid/List based on curated article count."""
    count = len(state.get("articles", []))
    layout_type: LayoutType
    if count == 1:
        layout_type = "Hero"
    elif count >= 4:
        layout_type = "Grid"
    else:
        layout_type = "List"

    return {
        "layout_type": layout_type,
        "phase": "determine_layout",
        "updated_at": _utc_now(),
    }


def build_news_graph():
    """Compile sequential graph: START -> fetch -> curate -> layout -> END."""
    builder = StateGraph(NewsGraphState)
    builder.add_node("fetch_news", fetch_news)
    builder.add_node("curate_content", curate_content)
    builder.add_node("determine_layout", determine_layout)

    builder.add_edge(START, "fetch_news")
    builder.add_edge("fetch_news", "curate_content")
    builder.add_edge("curate_content", "determine_layout")
    builder.add_edge("determine_layout", END)

    return builder.compile()


news_graph = build_news_graph()
