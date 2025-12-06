# Wiki Quiz App

This project implements a minimal Wiki Quiz application: a FastAPI backend that scrapes Wikipedia pages, generates a short multiple-choice quiz, and stores results; plus a simple static frontend (HTML) with two tabs: Generate and History.

# Here are some screenshort of the UI

![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)

Features included:

- Scrapes article HTML using BeautifulSoup
- Deterministic fallback quiz generator grounded in extracted content
- Persistence via SQLModel (default: SQLite; set `DATABASE_URL` to a Postgres URL for production)
- Frontend: `frontend/Quiz.html` and `frontend/quiz_history.html`
- Sample data in `sample_data/`
- Prompt template strings in `backend/app/llm.py` for wiring a real LLM via LangChain/OpenAI

Quick start (Windows, PowerShell):

1. Create and activate virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. (Optional) Use Postgres by setting `DATABASE_URL` environment variable

```powershell
setx DATABASE_URL "postgresql+psycopg2://user:pass@localhost/dbname"
```

4. Start the backend
```powershell
cd backend
```
```powershell
uvicorn app.main:app --reload --port 8000
```

5. Open the frontend files in a browser:

- `frontend/index.html` — Generate quiz
- `frontend/history.html` — View history

Notes:

- If you prefer to serve the frontend from the FastAPI app, add a static files mount. For test purposes opening the HTML files directly and running the backend locally works (CORS is enabled).
- To wire a real LLM via LangChain/OpenAI, modify `backend/app/llm.py` to call the chain using `QUIZ_PROMPT_TEMPLATE`. The fallback generator is used when no LLM is integrated.

What I implemented that meets the assessment:

- Scraping with BeautifulSoup (HTML only)
- Quiz generation (5–8 questions), options A–D, difficulty, and explanations
- Database storage and history API
- Frontend Generate and History pages with a Details modal
- Sample data and prompt templates

Next improvements (optional):

- Add an interactive "Take Quiz" mode with scoring
- Add URL preview (fetch title before processing)
- Store raw HTML in database (already stored)
- Add caching to prevent duplicate scraping (basic check implemented in `/api/generate`)
