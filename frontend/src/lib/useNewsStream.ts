"use client";

import { useCallback, useMemo, useState } from "react";

import {
  NewsState,
  StreamEvent,
  streamEventSchema,
} from "@/lib/news-schema";

type StreamStatus = "idle" | "streaming" | "done" | "error";

type UseNewsStreamResult = {
  state: NewsState | null;
  status: StreamStatus;
  error: string | null;
  start: () => Promise<void>;
};

const API_URL = process.env.NEXT_PUBLIC_NEWS_STREAM_URL ?? "http://localhost:8000/api/news/stream";

function splitNdjson(buffer: string): { lines: string[]; remainder: string } {
  const parts = buffer.split("\n");
  const remainder = parts.pop() ?? "";
  return { lines: parts.filter(Boolean), remainder };
}

export function useNewsStream(): UseNewsStreamResult {
  const [state, setState] = useState<NewsState | null>(null);
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(async () => {
    setError(null);
    setStatus("streaming");
    let didError = false;

    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });

    if (!response.ok || !response.body) {
      setStatus("error");
      setError(`Failed to stream news: ${response.status}`);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let partial = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }

      partial += decoder.decode(value, { stream: true });
      const { lines, remainder } = splitNdjson(partial);
      partial = remainder;

      for (const line of lines) {
        let parsed: StreamEvent;
        try {
          parsed = streamEventSchema.parse(JSON.parse(line));
        } catch {
          continue;
        }

        if (parsed.type === "state_update") {
          setState(parsed.payload);
        } else if (parsed.type === "error") {
          didError = true;
          setStatus("error");
          setError(parsed.payload.message);
          return;
        } else if (parsed.type === "done") {
          setStatus("done");
        }
      }
    }

    if (!didError) {
      setStatus("done");
    }
  }, []);

  return useMemo(
    () => ({
      state,
      status,
      error,
      start,
    }),
    [state, status, error, start],
  );
}
