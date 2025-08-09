from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import init_db
from .routers import experiments, generations, evaluations, analysis


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def create_app() -> FastAPI:
    app = FastAPI(title="LLM Content Evaluation")

    # API routers
    app.include_router(experiments.router)
    app.include_router(generations.router)
    app.include_router(evaluations.router)
    app.include_router(analysis.router)

    # Static files
    static_dir = BASE_DIR / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Pages
    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/setup", response_class=HTMLResponse)
    def setup(request: Request):
        return templates.TemplateResponse("setup.html", {"request": request})

    @app.get("/generate", response_class=HTMLResponse)
    def generate(request: Request):
        return templates.TemplateResponse("generate.html", {"request": request})

    @app.get("/evaluate", response_class=HTMLResponse)
    def evaluate(request: Request):
        return templates.TemplateResponse("evaluate.html", {"request": request})

    @app.get("/results", response_class=HTMLResponse)
    def results(request: Request):
        return templates.TemplateResponse("results.html", {"request": request})

    return app


# Initialize DB on import
init_db()
app = create_app()

