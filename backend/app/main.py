from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import select
from .database import create_db_and_engine, get_session
from .models import Article
from .schemas import GenerateRequest
from .scraper import scrape_article
from .llm import generate_quiz_from_text

app = FastAPI(title="Wiki Quiz API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_engine()


@app.post("/api/generate")
def generate(req: GenerateRequest):
    url = req.url.strip()
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")

    # check for cached record
    with get_session() as sess:
        stmt = select(Article).where(Article.url == url)
        existing = sess.exec(stmt).first()
        if existing:
            return JSONResponse(content=existing.to_dict())

    # scrape
    try:
        scraped = scrape_article(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")

    # generate quiz (LLM or fallback)
    generated = generate_quiz_from_text(scraped)

    # persist
    article = Article(
        url=url,
        title=scraped.get("title"),
        summary=scraped.get("summary"),
        key_entities=scraped.get("entities"),
        sections=scraped.get("sections"),
        quiz=generated.get("quiz"),
        related_topics=generated.get("related_topics"),
        raw_html=scraped.get("raw_html"),
    )

    with get_session() as sess:
        sess.add(article)
        sess.commit()
        sess.refresh(article)
        return JSONResponse(content=article.to_dict())


@app.get("/api/history")
def history():
    with get_session() as sess:
        stmt = select(Article).order_by(Article.created_at.desc())
        rows = sess.exec(stmt).all()
        return [r.summary_list() for r in rows]


@app.get("/api/history/{item_id}")
def history_item(item_id: int):
    with get_session() as sess:
        item = sess.get(Article, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        return JSONResponse(content=item.to_dict())
