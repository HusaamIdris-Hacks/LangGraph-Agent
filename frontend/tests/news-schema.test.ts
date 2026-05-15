import assert from "node:assert/strict";
import test from "node:test";

import { newsStateSchema, streamEventSchema } from "../src/lib/news-schema";

test("news state schema accepts valid payload", () => {
  const payload = {
    layout_type: "Grid",
    articles: [
      {
        title: "LangGraph improves deterministic state workflows",
        summary: "A new architecture guide helps teams stream state to UI clients.",
        source_url: "https://example.com/langgraph-ui-state",
      },
    ],
    run_id: "run_abc",
    updated_at: new Date().toISOString(),
    phase: "determine_layout",
  };

  const result = newsStateSchema.safeParse(payload);
  assert.equal(result.success, true);
});

test("news state schema accepts optional thumbnail_url", () => {
  const payload = {
    layout_type: "List",
    articles: [
      {
        title: "AI chip demand rises",
        summary: "Vendors report stronger orders for data-center accelerators.",
        source_url: "https://example.com/ai-chips",
        thumbnail_url: "https://example.com/ai-chips.jpg",
      },
    ],
    run_id: "run_thumb",
    updated_at: new Date().toISOString(),
    phase: "fetch_news",
  };

  const result = newsStateSchema.safeParse(payload);
  assert.equal(result.success, true);
});

test("stream event schema rejects invalid layout", () => {
  const event = {
    type: "state_update",
    payload: {
      layout_type: "Masonry",
      articles: [],
      run_id: "run_abc",
      updated_at: new Date().toISOString(),
      phase: "determine_layout",
    },
  };

  const result = streamEventSchema.safeParse(event);
  assert.equal(result.success, false);
});
