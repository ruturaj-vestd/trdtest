from __future__ import annotations

import hashlib
from dataclasses import dataclass

import httpx

from config import get_settings
from services.persistence import ResearchStore
from utils.cache import TTLCache


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0


class LLMRouter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = TTLCache("data/llm_cache")
        self.store = ResearchStore()

    def _cache_key(self, prompt: str, task: str) -> str:
        return hashlib.sha256(f"{task}:{prompt}".encode()).hexdigest()

    async def complete(self, prompt: str, task: str = "general") -> LLMResponse:
        key = self._cache_key(prompt, task)
        cached = self.cache.get(key)
        if cached:
            return LLMResponse(**cached)

        if self.settings.nvidia_api_key:
            response = await self._nvidia_glm(prompt)
        elif self.settings.use_ollama_fallback:
            response = await self._ollama(prompt)
        else:
            response = self._rules(prompt)

        self.cache.set(key, response.__dict__, ttl=self.settings.llm_cache_ttl_sec)
        self.store.log_llm_usage(
            response.provider,
            response.model,
            response.input_tokens,
            response.output_tokens,
            response.estimated_cost,
            task,
        )
        return response

    async def _nvidia_glm(self, prompt: str) -> LLMResponse:
        url = f"{self.settings.nvidia_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.nvidia_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.nvidia_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=35) as client:
            r = await client.post(url, headers=headers, json=payload)
        text = ""
        in_tok = max(1, len(prompt) // 4)
        out_tok = 0
        if r.is_success:
            data = r.json()
            choice = (data.get("choices") or [{}])[0]
            text = ((choice.get("message") or {}).get("content")) or ""
            usage = data.get("usage") or {}
            in_tok = usage.get("prompt_tokens", in_tok)
            out_tok = usage.get("completion_tokens", max(1, len(text) // 4))
        else:
            text = "NVIDIA GLM endpoint unavailable; fallback summary."
            out_tok = max(1, len(text) // 4)
        cost = in_tok * 0.000002 + out_tok * 0.000008
        return LLMResponse(
            text=text,
            provider="nvidia",
            model=self.settings.nvidia_model,
            input_tokens=int(in_tok),
            output_tokens=int(out_tok),
            estimated_cost=float(cost),
        )

    async def _ollama(self, prompt: str) -> LLMResponse:
        payload = {"model": self.settings.ollama_model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(f"{self.settings.ollama_base_url}/api/generate", json=payload)
        text = r.json().get("response", "") if r.is_success else "Ollama unavailable; fallback summary."
        return LLMResponse(text=text, provider="ollama", model=self.settings.ollama_model)

    def _rules(self, prompt: str) -> LLMResponse:
        p = prompt.lower()
        label = "neutral"
        if "beat" in p or "upgrade" in p:
            label = "bullish"
        elif "downgrade" in p or "miss" in p or "probe" in p:
            label = "bearish"
        return LLMResponse(text=f"Rules-based sentiment: {label}", provider="rules", model="deterministic-v1")
