import random
import string
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from .models import Evaluation, Generation, Experiment, Task


def _gen_blind_id(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "B-" + "".join(random.choice(alphabet) for _ in range(length))


def get_next_blind_item(db: Session, experiment_id: int) -> Optional[Tuple[str, str, str, str]]:
    """Return (blind_id, content, task_title, task_description) for next unevaluated generation."""
    # Find generations without evaluation
    subq = db.query(Evaluation.generation_id).filter(Evaluation.experiment_id == experiment_id)
    next_gen: Generation | None = (
        db.query(Generation)
        .filter(Generation.experiment_id == experiment_id)
        .filter(~Generation.id.in_(subq))
        .order_by(Generation.id.asc())
        .first()
    )
    if not next_gen:
        return None

    task = db.get(Task, next_gen.task_id)
    blind_id = _gen_blind_id()

    # Pre-create evaluation stub to reserve blind_id
    ev = Evaluation(
        generation_id=next_gen.id,
        experiment_id=experiment_id,
        blind_id=blind_id,
    )
    db.add(ev)
    db.commit()

    return blind_id, next_gen.generated_content or "", task.title if task else "", task.description if task else ""


def submit_evaluation(
    db: Session,
    experiment_id: int,
    blind_id: str,
    voice_match: int,
    coherence: int,
    engaging: int,
    meets_brief: int,
    overall_quality: int,
    edit_time_minutes: int,
    would_publish: str,
    notes: str,
) -> Evaluation:
    ev: Evaluation | None = (
        db.query(Evaluation)
        .filter(Evaluation.experiment_id == experiment_id, Evaluation.blind_id == blind_id)
        .first()
    )
    if not ev:
        raise ValueError("Blind evaluation not found")

    ev.voice_match = voice_match
    ev.coherence = coherence
    ev.engaging = engaging
    ev.meets_brief = meets_brief
    ev.overall_quality = overall_quality
    ev.edit_time_minutes = edit_time_minutes
    ev.would_publish = would_publish
    ev.notes = notes
    db.commit()
    db.refresh(ev)
    return ev


def evaluation_progress(db: Session, experiment_id: int) -> dict:
    total = db.query(Generation).filter(Generation.experiment_id == experiment_id).count()
    done = db.query(Evaluation).filter(Evaluation.experiment_id == experiment_id, Evaluation.overall_quality != None).count()  # noqa: E711
    return {"done": done, "total": total}

