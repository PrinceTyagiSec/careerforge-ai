import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class OllamaClient:
    """
    Local Ollama Client with graceful offline fallback.
    Never crashes when Ollama is stopped or unreachable.
    """
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout_seconds or settings.OLLAMA_TIMEOUT_SECONDS

    async def check_health(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {
                        "status": "Available",
                        "available_models": models,
                        "selected_model": self.model,
                        "error": None
                    }
        except Exception as e:
            pass

        return {
            "status": "Unavailable",
            "available_models": [],
            "selected_model": self.model,
            "error": "Ollama service is offline or not installed locally. Operating in deterministic fallback mode."
        }

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Sends prompt to Ollama if available; returns None if offline so caller uses deterministic logic.
        """
        if not settings.OLLAMA_ENABLED:
            return None

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    return res.json().get("response", "").strip()
        except Exception:
            return None

        return None
