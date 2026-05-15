"use client";

import { useEffect } from "react";

import { NewsRenderer } from "@/components/NewsRenderer";
import { getVisiblePhaseLabel } from "@/lib/phase-label";
import { useNewsStream } from "@/lib/useNewsStream";

export default function HomePage() {
  const { state, status, error, start } = useNewsStream();
  const isStreaming = status === "streaming";
  const phaseLabel = getVisiblePhaseLabel(state?.phase);
  const showLoading = isStreaming && !state?.articles?.length;

  useEffect(() => {
    void start();
  }, [start]);

  return (
    <main className="page-shell">
      <header className="page-header">
        <h1 className="page-title">Tech News</h1>
        <div className="header-actions">
          {isStreaming && phaseLabel ? <span className="phase-indicator">{phaseLabel}</span> : null}
          <button
            className="refresh-button"
            type="button"
            onClick={() => void start()}
            disabled={isStreaming}
            aria-label={isStreaming ? "Refreshing news" : "Refresh news"}
          >
            {isStreaming ? "···" : "Refresh"}
          </button>
        </div>
        {error ? <p className="error-message">{error}</p> : null}
      </header>

      {showLoading ? (
        <section className="empty-state" aria-busy="true">
          <span className="spinner" aria-hidden="true" />
          <p>{phaseLabel ?? "Loading"}</p>
        </section>
      ) : state ? (
        <NewsRenderer state={state} />
      ) : (
        <section className="empty-state">
          <span className="spinner" aria-hidden="true" />
          <p>Loading</p>
        </section>
      )}
    </main>
  );
}
