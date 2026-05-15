"use client";

import { useState } from "react";

type ArticleThumbnailProps = {
  src?: string | null;
  alt: string;
  className?: string;
};

export function ArticleThumbnail({ src, alt, className }: ArticleThumbnailProps) {
  const [failed, setFailed] = useState(false);

  if (!src || failed) {
    return null;
  }

  return (
    <img
      alt={alt}
      className={className ?? "news-card__thumb"}
      decoding="async"
      loading="lazy"
      onError={() => setFailed(true)}
      src={src}
    />
  );
}
