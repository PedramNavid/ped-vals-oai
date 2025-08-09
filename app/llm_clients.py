import os
import time
from typing import Dict, Tuple

from config import PRICING


def _safe_imports():
    openai = anthropic = genai = None
    try:
        import openai  # type: ignore
    except Exception:
        openai = None
    try:
        import anthropic  # type: ignore
    except Exception:
        anthropic = None
    try:
        import google.generativeai as genai  # type: ignore
    except Exception:
        genai = None
    return openai, anthropic, genai


class LLMClient:
    """LLM client wrapper with optional real SDK usage.

    Falls back to a stubbed response when SDKs/keys are unavailable, allowing
    local development without network calls.
    """

    def __init__(self):
        self.openai_sdk, self.anthropic_sdk, self.genai_sdk = _safe_imports()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")

        # Lazy SDK client init
        self._openai_client = None
        self._anthropic_client = None
        if self.genai_sdk and self.google_key:
            try:
                self.genai_sdk.configure(api_key=self.google_key)
            except Exception:
                pass

    def generate(self, provider: str, model: str, prompt: str, params: Dict) -> Tuple[str, Dict]:
        """Return generated text and metadata.

        metadata includes: latency_ms, prompt_tokens, completion_tokens, cost_usd
        """
        start_time = time.time()

        # Try real calls if possible, else stub
        try:
            if provider == "openai" and self.openai_sdk and self.openai_key:
                if self._openai_client is None:
                    self._openai_client = self.openai_sdk.OpenAI(api_key=self.openai_key)
                response = self._openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=params.get("temperature", 0.7),
                    max_tokens=params.get("max_tokens", 500),
                )
                content = response.choices[0].message.content
                usage = getattr(response, "usage", None)
                prompt_tokens = getattr(usage, "prompt_tokens", None) or 0
                completion_tokens = getattr(usage, "completion_tokens", None) or 0
            elif provider == "anthropic" and self.anthropic_sdk and self.anthropic_key:
                if self._anthropic_client is None:
                    self._anthropic_client = self.anthropic_sdk.Anthropic(api_key=self.anthropic_key)
                msg = self._anthropic_client.messages.create(
                    model=model,
                    max_tokens=params.get("max_tokens", 500),
                    temperature=params.get("temperature", 0.7),
                    messages=[{"role": "user", "content": prompt}],
                )
                # Anthropics SDK returns content as a list of blocks
                content = "".join([b.text for b in getattr(msg, "content", []) if hasattr(b, "text")])
                prompt_tokens = getattr(getattr(msg, "usage", None), "input_tokens", 0) or 0
                completion_tokens = getattr(getattr(msg, "usage", None), "output_tokens", 0) or 0
            elif provider == "google" and self.genai_sdk and self.google_key:
                model_obj = self.genai_sdk.GenerativeModel(model)
                resp = model_obj.generate_content(prompt)
                content = getattr(resp, "text", None) or "".join(getattr(resp, "candidates", []) or [])
                # Token accounting is not standardized here
                prompt_tokens = 0
                completion_tokens = 0
            else:
                raise RuntimeError("LLM SDK not available; using stub")
        except Exception:
            # Stubbed generation for offline/dev
            content = (
                f"[STUB:{provider}:{model}] Generated content for prompt (first 80 chars):\n"
                + prompt[:80]
                + ("..." if len(prompt) > 80 else "")
            )
            prompt_tokens = min(len(prompt) // 4, 512)
            completion_tokens = min(len(content) // 4, params.get("max_tokens", 500))

        latency_ms = (time.time() - start_time) * 1000
        cost = self._estimate_cost(provider, model, prompt_tokens, completion_tokens)
        metadata = {
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost,
        }

        return content, metadata

    def _estimate_cost(self, provider: str, model: str, in_tokens: int, out_tokens: int) -> float:
        prov = PRICING.get(provider, {})
        model_prices = prov.get(model, {})
        in_price = model_prices.get("input", 0.0)
        out_price = model_prices.get("output", 0.0)
        return (in_tokens / 1000.0) * in_price + (out_tokens / 1000.0) * out_price

