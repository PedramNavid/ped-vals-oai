from collections import defaultdict
from statistics import mean
from typing import Dict, List

from sqlalchemy.orm import Session

from .models import Evaluation, Generation


def summary(db: Session, experiment_id: int) -> Dict:
    evals: List[Evaluation] = (
        db.query(Evaluation)
        .filter(Evaluation.experiment_id == experiment_id, Evaluation.overall_quality != None)  # noqa: E711
        .all()
    )
    if not evals:
        return {"count": 0}
    scores = [e.overall_quality for e in evals if e.overall_quality is not None]
    return {
        "count": len(evals),
        "avg_overall": round(mean(scores), 3) if scores else None,
    }


def by_model(db: Session, experiment_id: int) -> Dict[str, Dict[str, float]]:
    rows = (
        db.query(Generation.model_name, Evaluation.overall_quality)
        .join(Evaluation, Evaluation.generation_id == Generation.id)
        .filter(Generation.experiment_id == experiment_id, Evaluation.overall_quality != None)  # noqa: E711
        .all()
    )
    agg: Dict[str, List[int]] = defaultdict(list)
    for model, score in rows:
        if score is not None:
            agg[model].append(score)
    return {m: {"avg_overall": round(mean(v), 3), "n": len(v)} for m, v in agg.items()}


def by_strategy(db: Session, experiment_id: int) -> Dict[str, Dict[str, float]]:
    rows = (
        db.query(Generation.prompt_strategy, Evaluation.overall_quality)
        .join(Evaluation, Evaluation.generation_id == Generation.id)
        .filter(Generation.experiment_id == experiment_id, Evaluation.overall_quality != None)  # noqa: E711
        .all()
    )
    agg: Dict[str, List[int]] = defaultdict(list)
    for strategy, score in rows:
        if score is not None:
            agg[str(strategy)].append(score)
    return {s: {"avg_overall": round(mean(v), 3), "n": len(v)} for s, v in agg.items()}


def by_task(db: Session, experiment_id: int) -> Dict[str, Dict[str, float]]:
    rows = (
        db.query(Generation.task_id, Evaluation.overall_quality)
        .join(Evaluation, Evaluation.generation_id == Generation.id)
        .filter(Generation.experiment_id == experiment_id, Evaluation.overall_quality != None)  # noqa: E711
        .all()
    )
    agg: Dict[str, List[int]] = defaultdict(list)
    for task_id, score in rows:
        if score is not None:
            agg[str(task_id)].append(score)
    return {t: {"avg_overall": round(mean(v), 3), "n": len(v)} for t, v in agg.items()}

