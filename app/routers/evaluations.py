from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..evaluation_service import get_next_blind_item, submit_evaluation, evaluation_progress
from ..schemas import EvaluationSubmit


router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.get("/next/{experiment_id}")
def next_item(experiment_id: int, db: Session = Depends(get_db)):
    item = get_next_blind_item(db, experiment_id)
    if not item:
        return {"done": True}
    blind_id, content, task_title, task_desc = item
    return {
        "blind_id": blind_id,
        "content": content,
        "task_title": task_title,
        "task_description": task_desc,
    }


@router.post("")
def submit(payload: EvaluationSubmit, experiment_id: int, db: Session = Depends(get_db)):
    ev = submit_evaluation(
        db,
        experiment_id=experiment_id,
        blind_id=payload.blind_id,
        voice_match=payload.voice_match,
        coherence=payload.coherence,
        engaging=payload.engaging,
        meets_brief=payload.meets_brief,
        overall_quality=payload.overall_quality,
        edit_time_minutes=payload.edit_time_minutes,
        would_publish=payload.would_publish,
        notes=payload.notes,
    )
    return {"ok": True, "id": ev.id}


@router.get("/progress/{experiment_id}")
def progress(experiment_id: int, db: Session = Depends(get_db)):
    return evaluation_progress(db, experiment_id)


@router.get("/{experiment_id}")
def list_evaluations(experiment_id: int, db: Session = Depends(get_db)):
    # Minimal listing to keep blind; not exposing mapping
    from ..models import Evaluation

    rows = (
        db.query(Evaluation)
        .filter(Evaluation.experiment_id == experiment_id, Evaluation.overall_quality != None)  # noqa: E711
        .order_by(Evaluation.id.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "blind_id": r.blind_id,
            "overall_quality": r.overall_quality,
        }
        for r in rows
    ]

