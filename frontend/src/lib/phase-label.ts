import { phaseTypeSchema } from "@/lib/news-schema";
import { z } from "zod";

type PhaseType = z.infer<typeof phaseTypeSchema>;

const PHASE_LABELS: Partial<Record<PhaseType, string>> = {
  fetch_news: "Fetching",
  curate_content: "Curating",
};

export function getVisiblePhaseLabel(phase: PhaseType | null | undefined): string | null {
  if (!phase || phase === "determine_layout") {
    return null;
  }

  return PHASE_LABELS[phase] ?? null;
}
