# CareerPilot AI

CareerPilot AI is a multi-agent career intelligence tool built with **LangGraph + FastAPI**. It analyzes a candidate's CV (PDF) against a target Job Description and produces a comprehensive, evidence-based career report with a deterministic match score, gap analysis, interview prep, roadmap, and actionable CV rewrites.

---

## Architecture

```
User (CV PDF + JD)
       │
       ▼
  FastAPI (app/)
       │ POST /api/analyze
       ▼
  LangGraph workflow
  ┌─────────────┐   ┌─────────────┐
  │ resume_agent│   │  job_agent  │  ← parallel fan-out
  └──────┬──────┘   └──────┬──────┘
         │                 │
         └────────┬────────┘
                  ▼
            skill_agent          ← deterministic 0–100 score
                  │
            gap_agent            ← web-search enriched
               ╱   ╲
  interview_agent  roadmap_agent ← parallel fan-out
               ╲   ╱
           clean_state
                  │
            report_agent         ← Markdown report + tables
                  │
         cv_suggestion_agent     ← optional bullet rewrites
                  │
                END
```

### Tech Stack

| Layer | Technology |
|---|---|
| AI orchestration | LangGraph, LangChain, Pydantic structured outputs |
| Backend | FastAPI 0.115, Uvicorn, PyMuPDF / pdfplumber |
| Frontend | React 19, Vite, TailwindCSS, shadcn/ui, lucide-react |
| Search | Tavily (primary) → Serper (fallback) |
| Deployment | Docker, Docker Compose, nginx |

---

## Scoring Method

The match score is computed **deterministically** in `skill_agent.py` (no LLM hallucination):

- Each **matched** skill contributes `100 / total_skills` points.
- Each **partial** match contributes half that.
- Missing skills contribute nothing.
- Score is clamped to `[0, 100]`.

The LLM is used only to produce the narrative explanation, not the numeric score.

---

## Project Structure

```
CareerAI/
├── app/
│   ├── agents/           # LangGraph node functions (one file per agent)
│   │   ├── agent_runner.py        # Transient-error detection + is_transient()
│   │   ├── cv_suggestion_agent.py # Optional CV bullet rewriter
│   │   ├── gap_agent.py           # Gap analysis + web search
│   │   ├── interview_agent.py     # Personalised interview questions
│   │   ├── job_agent.py           # Job description parser
│   │   ├── prompt_utils.py        # Anti-injection wrapper + ANTI_INJECTION_INSTRUCTION
│   │   ├── report_agent.py        # Final report + Markdown tables
│   │   ├── resume_agent.py        # CV parser
│   │   ├── roadmap_agent.py       # Career roadmap
│   │   └── skill_agent.py         # Deterministic skill match + score
│   ├── api/
│   │   ├── dependencies.py        # API-key auth middleware
│   │   └── routes.py              # /analyze, /analyze/stream, /compare, /interview
│   ├── graph/
│   │   ├── graph.py               # build_graph() with RetryPolicy
│   │   └── state.py               # CareerPilotState TypedDict
│   ├── schemas/models.py          # All Pydantic schemas
│   ├── services/
│   │   ├── analysis_service.py    # run_analysis() + run_analysis_stream()
│   │   ├── compare_service.py     # Concurrent multi-JD comparison
│   │   └── interview_service.py   # Interview answer evaluation
│   ├── tools/
│   │   ├── pdf_parser.py          # PyMuPDF → pdfplumber fallback
│   │   ├── web_search.py          # Tavily → Serper fallback
│   │   └── file_writer.py         # Optional report persistence
│   ├── config.py                  # Pydantic Settings (all env vars)
│   ├── llm.py                     # LLM factory (openai / google / anthropic)
│   └── main.py                    # FastAPI app + middleware
├── frontend/                      # React + Vite SPA
├── tests/                         # Pytest suite (no real API calls)
├── .env.example                   # All env vars documented
├── .ruff.toml                     # Ruff lint config
├── docker-compose.yml
├── Dockerfile.backend             # python:3.12-slim
├── Dockerfile.frontend            # node + nginx
├── requirements.txt               # Runtime deps
└── requirements.lock              # Pinned lockfile (pip-compile)
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your secrets.

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openai` | `openai` \| `google` \| `anthropic` |
| `LLM_MODEL` | `gpt-4o-mini` | Model name for the selected provider |
| `LLM_BASE_URL` | _(empty)_ | Optional custom base URL (e.g. OpenRouter) |
| `OPENAI_API_KEY` | _(required)_ | OpenAI API key |
| `GOOGLE_API_KEY` | _(optional)_ | Google API key |
| `ANTHROPIC_API_KEY` | _(optional)_ | Anthropic API key |
| `WEB_SEARCH_ENABLED` | `true` | Toggle web search enrichment |
| `TAVILY_API_KEY` | _(optional)_ | Tavily search key (primary) |
| `SERPER_API_KEY` | _(optional)_ | Serper search key (fallback) |
| `API_KEY` | _(empty)_ | Enable `X-API-Key` auth when set |
| `FORWARDED_ALLOW_IPS` | _(empty)_ | IPs trusted for `X-Forwarded-For` |
| `RATE_LIMIT_PER_MINUTE` | `10` | Max `/analyze` requests per IP per minute |
| `MAX_PDF_SIZE_MB` | `10` | Max upload size |
| `MAX_PDF_PAGES` | `50` | Max pages extracted from PDF |
| `MAX_RESUME_CHARS` | `30000` | Max chars kept from resume text |
| `MAX_JD_CHARS` | `15000` | Max chars accepted in job description |
| `SAVE_REPORTS` | `false` | Persist JSON + Markdown reports to disk |
| `REPORT_OUTPUT_DIR` | `data/reports` | Where to save reports |
| `MAX_AGENT_RETRIES` | `2` | Retry attempts per agent on transient errors |
| `AGENT_TIMEOUT_SECONDS` | `120` | Per-agent timeout |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG` | `false` | Enable debug mode |

---

## How to Run (Local Execution)

This application is designed to be run locally on your machine. You do not need to deploy it to any cloud provider.

### Option 1: Docker (Recommended for ease of use)

This is the simplest way to run the application, as it handles all dependencies automatically.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/M07ammd/CareerAI.git
    cd CareerAI
    ```

2.  **Configure Environment Variables:**
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file in a text editor and add your OpenAI API key:
    `OPENAI_API_KEY=sk-...`

3.  **Start the application:**
    ```bash
    docker compose up --build
    ```
    *(Wait a few minutes for the images to build and start. It's ready when you see both backend and frontend running successfully in the terminal.)*

4.  **Access the application:**
    - Open your browser and go to: `http://localhost` (Frontend UI)
    - Backend API is running at: `http://localhost:8000/api`
    - Interactive API Docs: `http://localhost:8000/docs`

5.  **Stop the application:**
    Press `Ctrl+C` in the terminal, then run:
    ```bash
    docker compose down
    ```

---

### Option 2: Local Development (Without Docker)

Use this option if you want to modify the code or prefer running things manually.

**1. Start the Backend:**
```bash
# Clone the repository
git clone https://github.com/M07ammd/CareerAI.git
cd CareerAI

# Create a virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.lock

# Configure Environment Variables
cp .env.example .env            
# Open .env and fill in OPENAI_API_KEY=sk-...

# Run the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*The backend server is now running on `http://localhost:8000`.*

**2. Start the Frontend:**
```bash
# Open a NEW terminal window/tab
cd CareerAI/frontend

# Install Node.js dependencies
npm install

# Start the Vite development server
npm run dev
```
*The frontend is now running on `http://localhost:5173`. Open this URL in your browser to use the app.*

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/analyze` | Full CV + JD analysis (JSON response) |
| `POST` | `/api/analyze/stream` | Same analysis, streamed as SSE events |
| `POST` | `/api/compare` | Compare CV against multiple JDs concurrently |
| `POST` | `/api/interview/evaluate` | Evaluate a candidate's interview answer |
| `GET` | `/api/health` | Health check |

### Example

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "cv_file=@resume.pdf" \
  -F "job_description=Senior ML Engineer with 5+ years Python..."
```

---

## Testing

```bash
pip install -r requirements-dev.txt

# All tests (no real API keys needed — LLMs are mocked)
pytest tests/ -v --ignore=tests/evaluation.py

# Lint
python -m ruff check app/ tests/
```

The suite covers:
- Pydantic schema validation
- Agent logic with mocked LLMs (retries, error handling)
- FastAPI endpoints (auth, rate limit, input validation)
- LangGraph graph routing
- Security controls (injection prevention, PII logging, API key auth)
