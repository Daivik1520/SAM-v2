"""
Simple persistent memory service for SAM Assistant
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class MemoryService:
    """Persistent memory storage to remember user facts and preferences."""

    def __init__(self, data_dir: Path, filename: str = "memory.json"):
        self.data_dir = data_dir
        self.filepath = self.data_dir / filename
        self.memories: List[Dict] = []
        self._load()

    def _load(self):
        try:
            if self.filepath.exists():
                with open(self.filepath, "r") as f:
                    self.memories = json.load(f)
            else:
                self.memories = []
        except Exception:
            # Start fresh if memory file is corrupted
            self.memories = []

    def _save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.memories, f, indent=2)
        except Exception:
            pass

    def add_memory(self, text: str, tags: Optional[List[str]] = None):
        entry = {
            "text": text.strip(),
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
        }
        self.memories.append(entry)
        # Keep memory bounded
        if len(self.memories) > 1000:
            self.memories = self.memories[-1000:]
        self._save()

    def get_memories_by_tag(self, tag: str) -> List[Dict]:
        return [m for m in self.memories if tag in m.get("tags", [])]

    def get_relevant_memories(self, query: str, top_k: int = 5) -> List[str]:
        """Very simple keyword-based retrieval for now."""
        q = set(query.lower().split())
        scored = []
        for m in self.memories:
            words = set(m["text"].lower().split())
            score = len(q.intersection(words))
            if score > 0:
                scored.append((score, m["text"]))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:top_k]]