from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..analysis_service import summary, by_model, by_strategy, by_task


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{experiment_id}/summary")
def get_summary(experiment_id: int, db: Session = Depends(get_db)):
    return summary(db, experiment_id)


@router.get("/{experiment_id}/by-model")
def model_stats(experiment_id: int, db: Session = Depends(get_db)):
    return by_model(db, experiment_id)


@router.get("/{experiment_id}/by-strategy")
def strategy_stats(experiment_id: int, db: Session = Depends(get_db)):
    return by_strategy(db, experiment_id)


@router.get("/{experiment_id}/by-task")
def task_stats(experiment_id: int, db: Session = Depends(get_db)):
    return by_task(db, experiment_id)

