import { ArticleThumbnail } from "@/components/ArticleThumbnail";
import { Article } from "@/lib/news-schema";

type HeroLayoutProps = {
  articles: Article[];
};

export function HeroLayout({ articles }: HeroLayoutProps) {
  const [lead, ...rest] = articles;
  if (!lead) return null;

  return (
    <section className="layout-hero">
      <article className="news-card news-card--hero">
        <ArticleThumbnail alt={lead.title} className="news-card__thumb news-card__thumb--hero" src={lead.thumbnail_url} />
        <h2 className="news-card__title">{lead.title}</h2>
        <p className="news-card__summary">{lead.summary}</p>
        <a
          className="source-link"
          href={lead.source_url}
          target="_blank"
          rel="noreferrer"
        >
          Read →
        </a>
      </article>

      {rest.length > 0 ? (
        <div className="layout-hero__secondary">
          {rest.map((article) => (
            <article className="news-card" key={article.source_url}>
              <ArticleThumbnail alt={article.title} src={article.thumbnail_url} />
              <h3 className="news-card__title">{article.title}</h3>
              <p className="news-card__summary">{article.summary}</p>
              <a className="source-link" href={article.source_url} target="_blank" rel="noreferrer">
                Read →
              </a>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
