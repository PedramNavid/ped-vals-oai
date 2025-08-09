import random
import time
from typing import Dict, Iterable, List, Tuple

from sqlalchemy.orm import Session

from .models import Experiment, Task, Generation, PromptStrategy, ModelProvider
from .llm_clients import LLMClient
from config import MODELS


def _build_prompt(task: Task, strategy: PromptStrategy, samples: List[str]) -> str:
    if strategy == PromptStrategy.STRUCTURED:
        return task.structured_prompt
    # example-based
    template = task.example_prompt_template or ""
    sample1 = samples[0] if samples else ""
    sample2 = samples[1] if len(samples) > 1 else sample1
    return template.replace("{sample1}", sample1).replace("{sample2}", sample2)


def start_generation(db: Session, experiment_id: int, run_all: bool = True, specific: Dict | None = None) -> Dict:
    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise ValueError("Experiment not found")

    tasks: List[Task] = db.query(Task).all()

    # Determine combinations
    combinations: List[Tuple[str, str, str]] = []  # (provider, model_name, strategy)
    if run_all:
        for provider, cfg in MODELS.items():
            model_name = cfg["model"]
            for strategy in (PromptStrategy.STRUCTURED.value, PromptStrategy.EXAMPLE_BASED.value):
                combinations.append((provider, model_name, strategy))
    else:
        if not specific:
            raise ValueError("specific_combination required when run_all is False")
        combinations.append((specific["provider"], specific["model"], specific["strategy"]))

    # Randomize combinations and tasks order
    random.shuffle(combinations)
    random.shuffle(tasks)

    client = LLMClient()
    progress = {"generated": 0, "total": len(combinations) * len(tasks), "cost_usd": 0.0}

    for provider, model_name, strategy_str in combinations:
        strategy = PromptStrategy(strategy_str)
        for task in tasks:
            prompt = _build_prompt(task, strategy, exp.baseline_samples or [])
            content, meta = client.generate(provider, model_name, prompt, MODELS[provider]["params"])
            gen = Generation(
                experiment_id=exp.id,
                task_id=task.id,
                model_provider=ModelProvider(provider),
                model_name=model_name,
                prompt_strategy=strategy,
                prompt_used=prompt,
                generated_content=content,
                generation_params=MODELS[provider]["params"],
                latency_ms=meta.get("latency_ms"),
                prompt_tokens=meta.get("prompt_tokens"),
                completion_tokens=meta.get("completion_tokens"),
                cost_usd=meta.get("cost_usd"),
            )
            db.add(gen)
            progress["generated"] += 1
            progress["cost_usd"] += meta.get("cost_usd", 0.0)
            db.commit()
            # Small delay to avoid clustering
            time.sleep(0.05)

    return progress


def list_generations(db: Session, experiment_id: int) -> List[Generation]:
    return (
        db.query(Generation)
        .filter(Generation.experiment_id == experiment_id)
        .order_by(Generation.id.asc())
        .all()
    )

