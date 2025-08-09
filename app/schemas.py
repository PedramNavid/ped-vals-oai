from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class ExperimentCreate(BaseModel):
    name: str
    description: Optional[str]
    baseline_samples: List[str]
    selected_models: List[Dict[str, str]]  # [{"provider": "openai", "model": "gpt-4"}]
    selected_strategies: List[str]
    selected_tasks: List[str]


class ExperimentOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    baseline_samples: List[str]
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class GenerationRequest(BaseModel):
    experiment_id: int
    run_all: bool = False
    specific_combination: Optional[Dict] = None


class EvaluationSubmit(BaseModel):
    blind_id: str
    voice_match: int
    coherence: int
    engaging: int
    meets_brief: int
    overall_quality: int
    edit_time_minutes: int
    would_publish: str
    notes: str


class BlindItem(BaseModel):
    blind_id: str
    content: str
    task_title: str
    task_description: str
    content_type: str

