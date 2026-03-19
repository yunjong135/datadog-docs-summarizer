import requests
from typing import Optional
from bs4 import BeautifulSoup

ALGOLIA_APP_ID = "EOIG7V0A2O"
ALGOLIA_INDEX = "docsearch_docs_prod"
ALGOLIA_SEARCH_API_KEY = "37251f5b8e70c2dc6a050bb67a0d3bec"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def search_via_algolia(query: str) -> Optional[list[dict]]:
    url = (
        f"https://{ALGOLIA_APP_ID}-dsn.algolia.net"
        f"/1/indexes/{ALGOLIA_INDEX}/query"
    )
    headers = {
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "X-Algolia-API-Key": ALGOLIA_SEARCH_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "hitsPerPage": 8,
        "attributesToRetrieve": ["title", "url", "content", "hierarchy"],
        "attributesToHighlight": ["title", "content"],
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        results = []
        seen_urls = set()

        for hit in data.get("hits", []):
            hit_url = hit.get("url", "")
            if not hit_url or hit_url in seen_urls:
                continue
            seen_urls.add(hit_url)

            hierarchy = hit.get("hierarchy", {})
            title = (
                hierarchy.get("lvl2")
                or hierarchy.get("lvl1")
                or hierarchy.get("lvl0")
                or hit.get("title", "")
            )

            highlight = hit.get("_highlightResult", {})
            content_highlight = highlight.get("content", {})
            excerpt = (
                content_highlight.get("value")
                or hit.get("content", "")
                or ""
            )
            excerpt = BeautifulSoup(excerpt, "html.parser").get_text()
            excerpt = excerpt[:200].strip()

            if "docs.datadoghq.com" not in hit_url:
                continue

            results.append({"title": title, "url": hit_url, "excerpt": excerpt})

        return results if results else None

    except Exception:
        return None


def search_via_crawl(query: str) -> list[dict]:
    search_url = f"https://docs.datadoghq.com/search/?query={requests.utils.quote(query)}"

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        results = []
        result_items = soup.select("article.result, .search-result, li.result")

        for item in result_items[:8]:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            if not href.startswith("http"):
                href = "https://docs.datadoghq.com" + href

            title = link_tag.get_text(strip=True) or href
            excerpt_tag = item.find("p") or item.find("span", class_="excerpt")
            excerpt = excerpt_tag.get_text(strip=True)[:200] if excerpt_tag else ""

            results.append({"title": title, "url": href, "excerpt": excerpt})

        return results

    except Exception as exc:
        raise RuntimeError(f"크롤링 검색 실패: {exc}") from exc


def search_docs(query: str) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("검색어를 입력해주세요.")

    results = search_via_algolia(query.strip())
    if results is not None:
        return results

    return search_via_crawl(query.strip())
