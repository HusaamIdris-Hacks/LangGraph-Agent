import os
from dotenv import load_dotenv

from typing import Any

import httpx

load_dotenv()


def main() -> None:
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        raise SystemExit("Missing NEWS_API_KEY in environment.")

    url = "https://newsapi.org/v2/top-headlines"
    base_params = {"from": "2026-04-22", "language": "en", "sortBy": "popularity", "q": "AI", "apiKey": api_key}
    tech_params = {**base_params, "category": "technology"}
    bus_params = {**base_params, "category": "business"}

    with httpx.Client(timeout=30) as client:
        tech_resp = client.get(url, params=tech_params)
        bus_resp = client.get(url, params=bus_params)
        tech_resp.raise_for_status()
        bus_resp.raise_for_status()

    tech_data: Any = tech_resp.json()
    bus_data: Any = bus_resp.json()

    tech_articles = tech_data.get("articles") or []
    bus_articles = bus_data.get("articles") or []

    merged_by_url: dict[str, Any] = {}
    for article in tech_articles + bus_articles:
        key = article.get("url") or article.get("title")
        if key:
            merged_by_url[key] = article

    merged_articles = list(merged_by_url.values())

    print("tech_status:", tech_data.get("status"), "tech_totalResults:", tech_data.get("totalResults"))
    print("business_status:", bus_data.get("status"), "business_totalResults:", bus_data.get("totalResults"))

    print("merged_articles_returned:", len(merged_articles))
    for i, a in enumerate(merged_articles[:10], start=1):
        print(f"{i}. {a.get('title')}")


if __name__ == "__main__":
    main()
