from __future__ import annotations

import os
from typing import Dict, List, Optional

from .memory import MemoryStore
from .ollama_client import OllamaClient


class MemGradOptimizer:
    """A minimal MemGrad-style optimizer using retrospective and prospective memory."""

    def __init__(
        self,
        memory_store: Optional[MemoryStore] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.store = memory_store or MemoryStore()
        self.client = OllamaClient(model_name=model_name, base_url=base_url)

    def record_failure(
        self,
        role: str,
        task: str,
        failure: str,
        resolution: str,
        trace: Optional[str] = None,
    ) -> None:
        self.store.add_entry(role=role, task=task, failure=failure, resolution=resolution, trace=trace)

    def retrospective_summary(self, role: str, limit: int = 10) -> str:
        return self.store.role_summary(role)

    def prospective_memory(self, role: str, new_failure: str) -> str:
        relevant = self.store.search(role=role, query_text=new_failure, limit=5)
        if not relevant:
            return "No relevant prior memory. Proceed with the current objective."
        blocks = []
        for entry in relevant:
            blocks.append(f"- When {entry.task}: {entry.failure}\n  Recommended fix: {entry.resolution}")
        return "\n".join(blocks)

    def optimize_prompt(self, role: str, base_prompt: str, task: str, failure: str) -> str:
        retrospective = self.retrospective_summary(role)
        prospective = self.prospective_memory(role, failure)
        memory_block = "\n".join([
            "Retrospective memory:",
            retrospective,
            "",
            "Prospective memory:",
            prospective,
        ])
        return self.client.improve_prompt(base_prompt=base_prompt, memory_text=memory_block)

    def build_role_prompt(self, role: str, base_prompt: str, task: str, failure: str) -> str:
        optimized = self.optimize_prompt(role, base_prompt, task, failure)
        return optimized.strip()

    def route_failure(self, failure: str, roles: List[str]) -> str:
        return self.client.route_role(failure=failure, roles=roles)


if __name__ == "__main__":
    store = MemoryStore()
    optimizer = MemGradOptimizer(memory_store=store)
    optimizer.record_failure(
        role="Programmer",
        task="Build a number guessing game",
        failure="The game logic wired choices incorrectly and produced wrong comparisons.",
        resolution="Validate the condition flow before finalizing the game loop and test representative inputs.",
    )
    print(optimizer.retrospective_summary("Programmer"))
