import json
import os
from typing import Optional, Dict, Any, List
from rapidfuzz import process, fuzz

class JQLTrainingLoader:
    def __init__(self, training_file: str):
        if not os.path.exists(training_file):
            raise FileNotFoundError(f"Training file not found: {training_file}")
        with open(training_file, "r", encoding="utf-8") as f:
            self.training_data: List[Dict[str, Any]] = json.load(f)

        # Flatten for fast lookup
        self._questions: List[str] = []
        self._map: Dict[str, Dict[str, Any]] = {}
        for entry in self.training_data:
            intent = entry.get("intent")
            jql = entry.get("jql")
            expected = entry.get("expected_response", "")
            for q in entry.get("questions", []):
                key = q.strip().lower()
                self._questions.append(key)
                self._map[key] = {"intent": intent, "jql": jql, "template": expected}

    def find(self, user_query: str, cutoff: float = 0.82) -> Optional[Dict[str, Any]]:
        """Return best match or None. cutoff in 0..1"""
        if not user_query:
            return None
        
        q = user_query.strip().lower()
        
        # First try exact match
        if q in self._map:
            return self._map[q]
        
        # Fuzzy with sensible cutoff
        match = process.extractOne(
            q,
            self._questions,
            scorer=fuzz.token_set_ratio,
            score_cutoff=int(cutoff * 100)
        )
        if not match:
            return None
        
        best_q, score, _ = match
        return self._map.get(best_q)