from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import requests


class OllamaClient:
    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None):
        self.model_name = model_name or os.environ.get("MODEL_NAME", "qwen2.5-coder:7b")
        self.base_url = (base_url or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")

    def chat(self, messages: List[Dict[str, str]], system: Optional[str] = None, temperature: float = 0.2) -> str:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system is not None:
            payload["system"] = system

        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        body = response.json()
        return body.get("message", {}).get("content", "")

    def summarize(self, text: str, task: str = "Summarize the following agent feedback") -> str:
        messages = [
            {"role": "user", "content": f"{task}\n\n{text}"},
        ]
        return self.chat(messages, system="You are a precise technical summarizer.")

    def improve_prompt(self, base_prompt: str, memory_text: str) -> str:
        system_prompt = (
            "You are a careful prompt optimizer. Incorporate only the most relevant recurring lessons "
            "into the prompt without making it bloated or repetitive. Preserve the task and the developer intent."
        )
        user_prompt = (
            "Base prompt:\n"
            f"{base_prompt}\n\n"
            "Relevant memory:\n"
            f"{memory_text}\n\n"
            "Return the revised prompt only."
        )
        return self.chat([{"role": "user", "content": user_prompt}], system=system_prompt, temperature=0.2)

    def route_role(self, failure: str, roles: List[str]) -> str:
        role_list = ", ".join(roles)
        system = "You are a role router. Choose the single most relevant role from the allowed set."
        user = (
            f"Failure description:\n{failure}\n\n"
            f"Allowed roles: {role_list}\n\n"
            "Return only the role name."
        )
        reply = self.chat([{"role": "user", "content": user}], system=system, temperature=0.0)
        return reply.strip()

    def parse_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start:end+1])
            return {"raw": text}
