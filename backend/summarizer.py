import os
import requests
import anthropic
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SUMMARY_PROMPT = (
    "다음 Datadog 공식 문서를 한국어로 요약해주세요. "
    "핵심 개념, 주요 기능, 설정 방법을 마크다운 형식으로 구조화해서 작성해주세요."
)

TAGS_TO_REMOVE = [
    "nav", "footer", "header", "aside",
    "script", "style", "noscript",
]


def crawl_page(url: str) -> tuple[str, str]:
    if not url.startswith("https://docs.datadoghq.com"):
        raise ValueError("Datadog 공식 문서 URL만 지원합니다 (docs.datadoghq.com).")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("페이지 로딩 시간이 초과되었습니다.")
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"페이지를 불러올 수 없습니다: HTTP {exc.response.status_code}")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"페이지 요청 실패: {exc}")

    soup = BeautifulSoup(response.text, "lxml")

    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    for selector in TAGS_TO_REMOVE:
        for element in soup.select(selector):
            element.decompose()

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id="main-content")
        or soup.find(id="content")
        or soup.find(class_="content")
    )

    if main_content:
        text = main_content.get_text(separator="\n", strip=True)
    else:
        body = soup.find("body") or soup
        text = body.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)

    if len(text) > 15000:
        text = text[:15000] + "\n\n[내용이 길어 일부 생략되었습니다]"

    return title, text


def summarize_with_claude(title: str, content: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

    client = anthropic.Anthropic(api_key=api_key)

    user_message = (
        f"{SUMMARY_PROMPT}\n\n"
        f"## 문서 제목\n{title}\n\n"
        f"## 문서 내용\n{content}"
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except anthropic.AuthenticationError:
        raise RuntimeError("Anthropic API 키가 유효하지 않습니다.")
    except anthropic.RateLimitError:
        raise RuntimeError("Anthropic API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
    except anthropic.APIError as exc:
        raise RuntimeError(f"Claude API 오류: {exc}")


def summarize_doc(url: str) -> dict:
    title, content = crawl_page(url)

    if not content.strip():
        raise RuntimeError("페이지에서 내용을 추출할 수 없습니다.")

    summary = summarize_with_claude(title, content)
    return {"summary": summary, "title": title, "url": url}
