# LLM Content Generation Evaluation App

A FastAPI web app to systematically evaluate which LLM (OpenAI, Anthropic, Google) and which prompting strategy produces the best marketing content, using blind human evaluations.

## Tech Stack
- Backend: FastAPI
- Database: SQLite + SQLAlchemy ORM
- Frontend: HTML/JS + Tailwind CSS (via CDN)
- LLM SDKs: `openai`, `anthropic`, `google-generativeai`
- Visualization: JSON summaries (Chart.js can be added later)

## Project Structure
```
llm-content-eval/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── models.py               # SQLAlchemy models
│   ├── database.py             # DB engine, session, init/load tasks
│   ├── schemas.py              # Pydantic schemas
│   ├── llm_clients.py          # LLM API wrapper with offline stub
│   ├── generation_service.py   # Generation logic
│   ├── evaluation_service.py   # Blind evaluation logic
│   ├── analysis_service.py     # Aggregations & summaries
│   └── routers/
│       ├── __init__.py
│       ├── experiments.py      # Experiment endpoints
│       ├── generations.py      # Generation endpoints
│       ├── evaluations.py      # Evaluation endpoints
│       └── analysis.py         # Analysis endpoints
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/
│   ├── base.html
│   ├── index.html              # Dashboard
│   ├── setup.html              # Experiment setup
│   ├── generate.html           # Run generations
│   ├── evaluate.html           # Blind evaluation
│   └── results.html            # Results & analysis
├── data/
│   ├── tasks.json              # Task definitions
│   └── database.db             # SQLite DB (created at runtime)
├── config.py                   # Models, pricing, DB URL
├── requirements.txt
└── .env                        # API keys (create locally)
```

## Prerequisites
- Python 3.10+
- Optional: virtual environment

## Install
```
pip install -r requirements.txt
```

## Configure Environment
Create a `.env` in the project root (keys are optional; without them, the app uses stubbed generations for local testing):
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

## Initialize Database and Load Tasks
```
python -c "from app.database import init_db; init_db()"
python -c "from app.database import load_tasks; load_tasks('data/tasks.json')"
```
This creates `data/database.db` and loads task definitions.

## Run the App
```
uvicorn app.main:app --reload
```
Open http://localhost:8000

## Usage Flow
1. Setup: Visit `/setup`. Paste 2+ writing samples (separated by blank lines) and create an experiment.
2. Generate: Visit `/generate`. Enter the experiment ID and Start All. If API keys are set, real SDKs are used; otherwise stubbed content is generated for flow testing.
3. Evaluate: Visit `/evaluate`. Enter the experiment ID, Load Next, and submit blind evaluations. The UI hides model/strategy/task provenance.
4. Results: Visit `/results`. Enter the experiment ID and load summary/by-model/by-strategy/by-task stats.

## API Endpoints (summary)
- Experiments: `POST /api/experiments`, `GET /api/experiments`, `GET /api/experiments/{id}`, `PUT /api/experiments/{id}/status`
- Generations: `POST /api/generations/start`, `GET /api/generations/progress/{experiment_id}`, `POST /api/generations/single`, `GET /api/generations/{experiment_id}`
- Evaluations: `GET /api/evaluations/next/{experiment_id}`, `POST /api/evaluations?experiment_id=...`, `GET /api/evaluations/progress/{experiment_id}`, `GET /api/evaluations/{experiment_id}`
- Analysis: `GET /api/analysis/{experiment_id}/summary`, `/by-model`, `/by-strategy`, `/by-task`

## Notes
- Offline-friendly: `llm_clients.py` falls back to stubbed responses if SDKs/keys are unavailable.
- Cost tracking: Estimated via `config.PRICING` and token usage where available (best-effort).
- Randomization: Generations randomize task/combination order and include small delays.
- Not yet implemented: CSV export and Chart.js visualizations (JSON summaries provided). Retry/backoff can be added for API errors.

## Troubleshooting
- Ensure `data/tasks.json` exists before loading tasks.
- If using SQLite, the app creates `data/database.db`. Verify the `data/` folder is writable.
- If SDK calls fail or no keys are set, stubbed content is returned to keep the flow working.

