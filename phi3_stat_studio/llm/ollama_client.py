"""Client for interacting with local Ollama models."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

import aiohttp

from ..config import CONFIG


class OllamaClient:
    """Minimal async client for Ollama chat endpoint."""

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        model_config = CONFIG.model
        self.base_url = base_url or model_config.base_url()
        self.model = model or model_config.model

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=CONFIG.model.request_timeout)) as session:
            url = f"{self.base_url}/api/generate"
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                result = await response.text()
                data = json.loads(result)
                return data.get("response", "")

    def generate_sync(self, prompt: str, system_prompt: str | None = None) -> str:
        return asyncio.get_event_loop().run_until_complete(self.generate(prompt, system_prompt))


