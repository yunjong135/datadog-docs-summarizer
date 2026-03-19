import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def search_via_duckduckgo(query: str) -> list[dict]:
    """DuckDuckGo HTML 검색으로 docs.datadoghq.com 문서를 찾습니다."""
    search_query = f"site:docs.datadoghq.com {query}"
    url = f"https://html.duckduckgo.com/html/?q={quote(search_query)}"

    response = requests.get(url, headers=HEADERS, timeout=8)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    results = []

    for item in soup.select(".result__body")[:8]:
        title_tag = item.select_one(".result__title a")
        snippet_tag = item.select_one(".result__snippet")

        if not title_tag:
            continue

        href = title_tag.get("href", "")
        # DuckDuckGo redirect URL에서 실제 URL 추출
        if "uddg=" in href:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(href)
            real_url = parse_qs(parsed.query).get("uddg", [""])[0]
        else:
            real_url = href

        if "docs.datadoghq.com" not in real_url:
            continue

        title = title_tag.get_text(strip=True)
        excerpt = snippet_tag.get_text(strip=True)[:200] if snippet_tag else ""

        results.append({"title": title, "url": real_url, "excerpt": excerpt})

    return results


def search_via_google(query: str) -> list[dict]:
    """Google 검색으로 docs.datadoghq.com 문서를 찾습니다 (fallback)."""
    search_query = f"site:docs.datadoghq.com {query}"
    url = f"https://www.google.com/search?q={quote(search_query)}&num=8"

    headers = {**HEADERS, "Accept-Language": "en-US,en;q=0.9"}
    response = requests.get(url, headers=headers, timeout=8)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    results = []

    for g in soup.select("div.g, div[data-sokoban-container]")[:8]:
        title_tag = g.select_one("h3")
        link_tag = g.select_one("a[href]")
        snippet_tag = g.select_one("div[data-sncf], span[data-dtld]") or g.select_one(".VwiC3b")

        if not title_tag or not link_tag:
            continue

        href = link_tag.get("href", "")
        if not href.startswith("https://docs.datadoghq.com"):
            continue

        title = title_tag.get_text(strip=True)
        excerpt = snippet_tag.get_text(strip=True)[:200] if snippet_tag else ""

        results.append({"title": title, "url": href, "excerpt": excerpt})

    return results


def search_docs(query: str) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("검색어를 입력해주세요.")

    query = query.strip()

    # 1차: DuckDuckGo
    try:
        results = search_via_duckduckgo(query)
        if results:
            return results
    except Exception:
        pass

    # 2차 fallback: Google
    try:
        results = search_via_google(query)
        if results:
            return results
    except Exception:
        pass

    return []
