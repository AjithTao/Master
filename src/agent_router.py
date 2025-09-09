from __future__ import annotations
from typing import Literal
import re

def route(query: str) -> Literal["JIRA","CONFLUENCE","BOTH"]:
    q = query.lower()
    jira_kw = any(k in q for k in ["story","stories","ticket","bug","sprint","backlog","issue","epic","board","velocity","jira"])    
    conf_kw = any(k in q for k in ["confluence","doc","page","kt","recording","wiki","design","spec","minutes","mom","decision"])    
    if jira_kw and conf_kw:
        return "BOTH"
    if jira_kw:
        return "JIRA"
    if conf_kw:
        return "CONFLUENCE"
    # default: try JIRA, it usually provides status
    return "JIRA"

def parse_assignee(query: str) -> str | None:
    # Special case for known team members - check first
    query_lower = query.lower()
    if 'ashwin' in query_lower:
        return 'Ashwin Thyagarajan'
    elif 'karthikeya' in query_lower:
        return 'Karthikeya'
    elif 'saravanan' in query_lower:
        return 'SARAVANAN NP'
    
    # Enhanced heuristic: extract a name after various patterns
    patterns = [
        r"(?:by|worked by|assigned to|issues by|tasks by|work by)\s+([A-Za-z][A-Za-z\s.'-]{1,40})",
        r"(?:Ashwin|Karthikeya|SARAVANAN|assignee)\s+([A-Za-z][A-Za-z\s.'-]{1,40})",
        r"([A-Za-z][A-Za-z\s.'-]{1,40})\s+(?:issues|tasks|work|assigned)"
    ]
    
    for pattern in patterns:
        m = re.search(pattern, query, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            # Filter out common words and phrases that aren't names
            excluded_words = [
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'working', 'on', 'issues', 'tasks', 'work', 'assigned', 'show', 'me', 'recent', 'current', 'sprint',
                'all', 'some', 'any', 'every', 'each', 'both', 'either', 'neither', 'this', 'that', 'these', 'those'
            ]
            
            # Check if the extracted name contains any excluded words
            name_words = name.lower().split()
            if not any(word in excluded_words for word in name_words):
                return name
    
    return None

def wants_stories_only(query: str) -> bool:
    return "story" in query.lower() or "stories" in query.lower()
