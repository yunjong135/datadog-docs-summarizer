from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

from search import search_docs
from summarizer import summarize_doc

load_dotenv()


class SearchRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("검색어는 비워둘 수 없습니다.")
        return v.strip()


class SearchResultItem(BaseModel):
    title: str
    url: str
    excerpt: str


class SearchResponse(BaseModel):
    results: list[SearchResultItem]


class SummarizeRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def url_must_be_datadog_docs(cls, v: str) -> str:
        if "docs.datadoghq.com" not in v:
            raise ValueError("Datadog 공식 문서 URL만 지원합니다 (docs.datadoghq.com).")
        return v


class SummarizeResponse(BaseModel):
    summary: str
    title: str
    url: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Datadog Docs Summarizer API",
    description="Datadog 공식 문서를 검색하고 Claude AI로 한글 요약을 제공합니다.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.post("/api/search", response_model=SearchResponse, tags=["Docs"])
def search(request: SearchRequest):
    try:
        results = search_docs(request.query)
        return SearchResponse(results=results)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {exc}")


@app.post("/api/summarize", response_model=SummarizeResponse, tags=["Docs"])
def summarize(request: SummarizeRequest):
    try:
        result = summarize_doc(request.url)
        return SummarizeResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"요약 중 오류가 발생했습니다: {exc}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
