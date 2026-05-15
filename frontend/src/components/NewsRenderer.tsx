import { GridLayout } from "@/components/layouts/GridLayout";
import { HeroLayout } from "@/components/layouts/HeroLayout";
import { ListLayout } from "@/components/layouts/ListLayout";
import { NewsState } from "@/lib/news-schema";

type NewsRendererProps = {
  state: NewsState;
};

export function NewsRenderer({ state }: NewsRendererProps) {
  if (state.layout_type === "Hero") {
    return <HeroLayout articles={state.articles} />;
  }

  if (state.layout_type === "Grid") {
    return <GridLayout articles={state.articles} />;
  }

  return <ListLayout articles={state.articles} />;
}
