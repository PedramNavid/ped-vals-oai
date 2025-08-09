from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..generation_service import start_generation, list_generations
from ..schemas import GenerationRequest


router = APIRouter(prefix="/api/generations", tags=["generations"])


@router.post("/start")
def start(payload: GenerationRequest, db: Session = Depends(get_db)):
    progress = start_generation(db, payload.experiment_id, payload.run_all, payload.specific_combination)
    return progress


@router.get("/progress/{experiment_id}")
def progress(experiment_id: int, db: Session = Depends(get_db)):
    gens = list_generations(db, experiment_id)
    return {"generated": len(gens)}


@router.post("/single")
def generate_single(payload: dict, db: Session = Depends(get_db)):
    # Thin wrapper around start with run_all=False
    req = GenerationRequest(**payload, run_all=False)
    return start_generation(db, req.experiment_id, False, req.specific_combination)


@router.get("/{experiment_id}")
def list_for_experiment(experiment_id: int, db: Session = Depends(get_db)):
    gens = list_generations(db, experiment_id)
    # Do not return prompts to keep it blind
    return [
        {
            "id": g.id,
            "task_id": g.task_id,
            "model_provider": str(g.model_provider),
            "model_name": g.model_name,
            "prompt_strategy": str(g.prompt_strategy),
            "timestamp": g.timestamp,
        }
        for g in gens
    ]

