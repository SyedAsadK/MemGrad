from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    role: str
    task: str
    failure: str
    resolution: str
    created_at: str
    trace: Optional[str] = None

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            role=row["role"],
            task=row["task"],
            failure=row["failure"],
            resolution=row["resolution"],
            created_at=row["created_at"],
            trace=row.get("trace"),
        )


class MemoryStore:
    """Persist a lightweight retrospective/prospective memory store in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            db_dir = os.path.join(repo_root, ".local_cache", "memgrad")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "memgrad.sqlite")
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    task TEXT NOT NULL,
                    failure TEXT NOT NULL,
                    resolution TEXT NOT NULL,
                    trace TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_entry(
        self,
        role: str,
        task: str,
        failure: str,
        resolution: str,
        trace: Optional[str] = None,
    ) -> MemoryEntry:
        created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO memories (role, task, failure, resolution, trace, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (role, task, failure, resolution, trace, created_at),
            )
            conn.commit()
        return MemoryEntry(role, task, failure, resolution, created_at, trace)

    def list_entries(self, role: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        query = "SELECT role, task, failure, resolution, trace, created_at FROM memories"
        params: List[Any] = []
        if role is not None:
            query += " WHERE role = ?"
            params.append(role)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()

        return [MemoryEntry.from_row({
            "role": row[0],
            "task": row[1],
            "failure": row[2],
            "resolution": row[3],
            "trace": row[4],
            "created_at": row[5],
        }) for row in rows]

    def search(self, role: str, query_text: str, limit: int = 10) -> List[MemoryEntry]:
        entries = self.list_entries(role=role, limit=limit)
        if not query_text:
            return entries

        lower_query = query_text.lower()
        return [
            entry for entry in entries
            if lower_query in (entry.failure + " " + entry.resolution + " " + entry.task).lower()
        ]

    def role_summary(self, role: str) -> str:
        entries = self.list_entries(role=role, limit=10)
        if not entries:
            return "No prior experience recorded for this role."
        blocks = []
        for entry in entries:
            blocks.append(f"- Failure: {entry.failure}\n  Resolution: {entry.resolution}")
        return "\n".join(blocks)

    def as_json(self) -> str:
        entries = self.list_entries(limit=100)
        return json.dumps([asdict(entry) for entry in entries], indent=2)
