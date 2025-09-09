import os
from typing import List, Dict

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # Optional dependency


def _format_list(results: List[Dict]) -> str:
    lines: List[str] = []
    for i in results[:10]:
        key = i.get("key", "")
        fields = i.get("fields", {})
        summary = fields.get("summary", "")
        status = (fields.get("status") or {}).get("name", "")
        assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
        lines.append(f"- {key} — {summary} (Status: {status}, Assignee: {assignee})")
    return "\n".join(lines)


def summarize(user_query: str, results: List[Dict], response_type: str) -> str:
    """Summarize deterministically with optional LLM enhancement."""
    # Deterministic baseline
    if response_type == "count":
        count = len(results)
        base = f"Found {count} matching issues."
    else:
        base = _format_list(results)

    # Optional LLM overlay
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        # No LLM available; return deterministic output
        return base

    client = OpenAI(api_key=api_key)
    if response_type == "count":
        user = (
            f"User asked: {user_query}\n"
            f"Jira returned {len(results)} matching issues.\n"
            "Write a crisp leadership-style summary in 1–2 lines."
        )
    else:
        user = (
            f"User asked: {user_query}\n"
            "Top results:\n" + base + "\n"
            "Provide a short leadership summary (1–3 lines)."
        )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Jira leadership assistant. Be concise, factual, and avoid speculation."},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        txt = resp.choices[0].message.content.strip()
        return f"{base}\n\nLeadership Note: {txt}" if response_type != "count" else txt
    except Exception:
        return base


