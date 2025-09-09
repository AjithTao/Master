import re
from typing import Dict, List


PROJECT_NAME_MAP = {
    "service advisory": "SA",
    "sa": "SA",
    "docs": "DOCS",
    "doc": "DOCS",
    "ndp": "NDP",
    "is": "IS",
    "finops": "FINOPS",
    "crm": "CRM",
}

ISSUETYPE_SET = {"story", "bug", "task", "epic", "sub-task", "subtask"}
PRIORITY_SET = {"highest", "high", "medium", "low"}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _parse_date_range(uq: str) -> str | None:
    if any(x in uq for x in ["this week", "current week"]):
        return "-7d"
    if "last week" in uq:
        return "-7d"
    if "last month" in uq:
        return "-30d"
    if "today" in uq:
        return "-1d"
    if "this month" in uq:
        return "startOfMonth()"
    if "last 7 days" in uq:
        return "-7d"
    if "last 30 days" in uq:
        return "-30d"
    return None


def _parse_sprint(uq: str) -> str | None:
    m = re.search(r"sprint\s*(\d+)", uq)
    return m.group(1) if m else None


def _parse_project(uq: str, *, jira_client=None) -> str | None:
    for key, val in PROJECT_NAME_MAP.items():
        if key in uq:
            return val
    # Prefer exact match against known Jira project keys
    try:
        if jira_client:
            keys = jira_client.get_known_project_keys() or []
            keys_lower = {k.lower(): k for k in keys}
            # Match whole word tokens only
            for token in re.findall(r"\b[\w-]{2,10}\b", uq):
                if token in keys_lower:
                    return keys_lower[token]
    except Exception:
        pass
    # Heuristic: avoid mapping the English word 'is'
    return None


def _parse_assignee(uq: str, known_assignees: List[str]) -> str | None:
    # Prefer full display name match, fallback contains match
    for name in known_assignees:
        ln = (name or "").lower()
        if ln and ln in uq:
            return name
    return None


def _parse_issuetype(uq: str) -> str | None:
    for t in ISSUETYPE_SET:
        if t in uq:
            return "Sub-task" if t in {"sub-task", "subtask"} else t.title()
    return None


def _parse_priority(uq: str) -> str | None:
    for p in PRIORITY_SET:
        if p in uq:
            return p.title()
    return None


def _parse_label(uq: str) -> str | None:
    m = re.search(r"label\s+([\w-]+)", uq)
    return m.group(1) if m else None


def _parse_component(uq: str) -> str | None:
    m = re.search(r"component\s+([\w-]+)", uq)
    return m.group(1) if m else None


def _parse_status(uq: str) -> str | None:
    # Simple status phrases
    status_map = {
        "open": "Open",
        "in progress": "In Progress",
        "blocked": "Blocked",
        "done": "Done",
        "closed": "Done",
        "reopened": "Reopened",
        "ready for qa": "Ready for QA",
    }
    for k, v in status_map.items():
        if k in uq:
            return v
    return None


def extract_entities(user_query: str, *, jira_client) -> Dict[str, str]:
    uq = _normalize(user_query)
    try:
        known_assignees = jira_client.get_known_assignee_names() or []
    except Exception:
        known_assignees = []

    entities: Dict[str, str] = {}

    prj = _parse_project(uq, jira_client=jira_client)
    if prj:
        entities["PROJECT"] = prj

    assignee = _parse_assignee(uq, known_assignees)
    if assignee:
        entities["ASSIGNEE"] = assignee

    dt = _parse_date_range(uq)
    if dt:
        entities["DATE_RANGE"] = dt

    sp = _parse_sprint(uq)
    if sp:
        entities["SPRINT"] = sp

    it = _parse_issuetype(uq)
    if it:
        entities["ISSUETYPE"] = it

    st = _parse_status(uq)
    if st:
        entities["STATUS"] = st

    pr = _parse_priority(uq)
    if pr:
        entities["PRIORITY"] = pr

    lb = _parse_label(uq)
    if lb:
        entities["LABEL"] = lb

    comp = _parse_component(uq)
    if comp:
        entities["COMPONENT"] = comp

    # Version like 1.2.3 or 1.2
    m = re.search(r"(?:release|version)\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)", uq)
    if m:
        entities["VERSION"] = m.group(1)

    return entities


def fill_defaults(intent: dict, entities: Dict[str, str]) -> Dict[str, str]:
    out = dict(entities)
    name = intent.get("intent", "")
    # Intent-based defaults
    if "high_priority_bugs" in name:
        out.setdefault("PRIORITY", "High")
        out.setdefault("ISSUETYPE", "Bug")
    if "recently_updated" in name:
        out.setdefault("DATE_RANGE", "-7d")
    if "open_bugs_project" in name:
        out.setdefault("ISSUETYPE", "Bug")
    return out


