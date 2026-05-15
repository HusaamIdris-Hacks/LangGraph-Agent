import { ArticleThumbnail } from "@/components/ArticleThumbnail";
import { Article } from "@/lib/news-schema";

type ListLayoutProps = {
  articles: Article[];
};

export function ListLayout({ articles }: ListLayoutProps) {
  return (
    <section className="layout-list">
      {articles.map((article) => (
        <article className="news-card" key={article.source_url}>
          <ArticleThumbnail alt={article.title} src={article.thumbnail_url} />
          <h3 className="news-card__title">{article.title}</h3>
          <p className="news-card__summary">{article.summary}</p>
          <a
            className="source-link"
            href={article.source_url}
            target="_blank"
            rel="noreferrer"
          >
            Read →
          </a>
        </article>
      ))}
    </section>
  );
}
