from __future__ import annotations

import hashlib
import json
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

        if self.settings.openai_api_key:
            response = await self._openai(prompt)
        elif self.settings.use_ollama_fallback:
            response = await self._ollama(prompt)
        else:
            response = self._rules(prompt)

        self.cache.set(key, response.__dict__, ttl=self.settings.llm_cache_ttl_sec)
        self.store.log_llm_usage(response.provider, response.model, response.input_tokens, response.output_tokens, response.estimated_cost, task)
        return response

    async def _openai(self, prompt: str) -> LLMResponse:
        # minimal HTTP usage to remain provider-agnostic.
        headers = {"Authorization": f"Bearer {self.settings.openai_api_key}"}
        payload = {"model": self.settings.openai_model, "input": prompt}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
        text = ""
        if r.is_success:
            data = r.json()
            text = data.get("output_text", "") or json.dumps(data)[:500]
        else:
            text = "OpenAI unavailable; fallback summary."
        in_tok = max(1, len(prompt) // 4)
        out_tok = max(1, len(text) // 4)
        cost = in_tok * 0.000002 + out_tok * 0.000008
        return LLMResponse(text=text, provider="openai", model=self.settings.openai_model, input_tokens=in_tok, output_tokens=out_tok, estimated_cost=cost)

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
