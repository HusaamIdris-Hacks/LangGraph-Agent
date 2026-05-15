import { z } from "zod";

export const layoutTypeSchema = z.enum(["Hero", "Grid", "List"]);
export const phaseTypeSchema = z.enum([
  "fetch_news",
  "curate_content",
  "determine_layout",
]);

export const articleSchema = z.object({
  title: z.string().min(1),
  summary: z.string().min(1),
  source_url: z.string().url(),
  thumbnail_url: z.string().url().optional().nullable(),
});

export const newsStateSchema = z.object({
  layout_type: layoutTypeSchema,
  articles: z.array(articleSchema),
  run_id: z.string().optional().nullable(),
  updated_at: z.string(),
  phase: phaseTypeSchema.optional().nullable(),
});

export const errorPayloadSchema = z.object({
  message: z.string(),
  run_id: z.string(),
  details: z.array(z.record(z.any())).optional().nullable(),
});

export const donePayloadSchema = z.object({
  run_id: z.string(),
});

export const stateUpdateEventSchema = z.object({
  type: z.literal("state_update"),
  payload: newsStateSchema,
});

export const errorEventSchema = z.object({
  type: z.literal("error"),
  payload: errorPayloadSchema,
});

export const doneEventSchema = z.object({
  type: z.literal("done"),
  payload: donePayloadSchema,
});

export const streamEventSchema = z.discriminatedUnion("type", [
  stateUpdateEventSchema,
  errorEventSchema,
  doneEventSchema,
]);

export type LayoutType = z.infer<typeof layoutTypeSchema>;
export type Article = z.infer<typeof articleSchema>;
export type NewsState = z.infer<typeof newsStateSchema>;
export type StreamEvent = z.infer<typeof streamEventSchema>;
