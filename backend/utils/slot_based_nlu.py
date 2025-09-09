import re
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

@dataclass
class SlotValue:
    """Represents a slot value with confidence and alternatives"""
    value: str
    confidence: float
    alternatives: List[str] = None
    raw_text: str = None

@dataclass
class ExtractedSlots:
    """Container for all extracted slots from user query"""
    project: Optional[SlotValue] = None
    board: Optional[SlotValue] = None
    sprint: Optional[SlotValue] = None
    assignee: Optional[SlotValue] = None
    issuetype: Optional[SlotValue] = None
    status: Optional[SlotValue] = None
    status_category: Optional[SlotValue] = None
    priority: Optional[SlotValue] = None
    component: Optional[SlotValue] = None
    label: Optional[SlotValue] = None
    epic: Optional[SlotValue] = None
    version: Optional[SlotValue] = None
    fix_version: Optional[SlotValue] = None
    date_range: Optional[SlotValue] = None
    text: Optional[SlotValue] = None
    field: Optional[SlotValue] = None
    quantity: Optional[SlotValue] = None
    order: Optional[SlotValue] = None

class SlotBasedNLU:
    """Slot-based Natural Language Understanding for Jira queries"""
    
    def __init__(self, jira_client=None):
        self.jira_client = jira_client
        self.context = {
            'project': None,
            'board': None,
            'sprint': None
        }
        # Known Jira project keys for the current session (set by backend when configured)
        self.known_project_keys: Set[str] = set()
        
        # Common patterns and mappings
        self.project_pattern = re.compile(r'\b([A-Z]{2,5})\b', re.IGNORECASE)
        self.common_words = {
            'give','me','show','get','find','open','closed','all','the','and','or','for','with','in','on','at','to','from','by','how','many','what','is','are','can','you','tell','about',
            # non-project nouns frequently present in queries
            'bug','bugs','defect','defects','issue','issues','ticket','tickets','item','items',
            'story','stories','task','tasks','sprint','current','project','projects'
        }
        
        # Issuetype mappings
        self.issuetype_mappings = {
            'story': 'Story',
            'stories': 'Story',
            'bug': 'Bug',
            'bugs': 'Bug',
            'defect': 'Bug',
            'defects': 'Bug',
            'task': 'Task',
            'tasks': 'Task',
            'epic': 'Epic',
            'epics': 'Epic',
            'subtask': 'Sub-task',
            'sub-task': 'Sub-task',
            'subtasks': 'Sub-task',
            'sub-tasks': 'Sub-task'
        }
        
        # Status mappings
        self.status_mappings = {
            'todo': 'To Do',
            'to do': 'To Do',
            'open': 'To Do',
            'in progress': 'In Progress',
            'in-progress': 'In Progress',
            'progress': 'In Progress',
            'done': 'Done',
            'closed': 'Done',
            'completed': 'Done',
            'finished': 'Done'
        }
        
        # Status category mappings
        self.status_category_mappings = {
            'todo': 'To Do',
            'to do': 'To Do',
            'open': 'To Do',
            'in progress': 'In Progress',
            'in-progress': 'In Progress',
            'progress': 'In Progress',
            'done': 'Done',
            'closed': 'Done',
            'completed': 'Done',
            'finished': 'Done'
        }
        
        # Priority mappings
        self.priority_mappings = {
            'highest': 'Highest',
            'critical': 'Critical',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low',
            'lowest': 'Lowest',
            'urgent': 'Critical',
            'blocker': 'Highest'
        }
        
        # Sprint patterns
        self.sprint_patterns = {
            'current': 'openSprints()',
            'this sprint': 'openSprints()',
            'active': 'openSprints()',
            'last': 'closedSprints()',
            'previous': 'closedSprints()',
            'closed': 'closedSprints()',
            'future': 'futureSprints()',
            'upcoming': 'futureSprints()'
        }
        
        # Date range patterns
        self.date_patterns = {
            'today': 'startOfDay()',
            'yesterday': 'startOfDay(-1)',
            'this week': 'startOfWeek()',
            'last week': 'startOfWeek(-1)',
            'this month': 'startOfMonth()',
            'last month': 'startOfMonth(-1)',
            'last 30 days': '-30d',
            'last 7 days': '-7d',
            'this year': 'startOfYear()',
            'last year': 'startOfYear(-1)'
        }
        
        # Order patterns
        self.order_patterns = {
            'oldest': 'created ASC',
            'newest': 'created DESC',
            'recent': 'updated DESC',
            'priority': 'priority DESC',
            'assignee': 'assignee ASC',
            'status': 'status ASC',
            'due date': 'duedate ASC',
            'story points': 'Story Points DESC'
        }
        
        # Quantity patterns
        self.quantity_patterns = {
            'top': 'TOP',
            'first': 'TOP',
            'last': 'BOTTOM',
            'bottom': 'BOTTOM'
        }

    def extract_slots(self, query: str) -> ExtractedSlots:
        """Extract all slots from user query with improved precision"""
        query_lower = query.lower()
        slots = ExtractedSlots()
        
        # Extract text search first (highest priority)
        slots.text = self._extract_text_search(query)
        
        # Extract project
        slots.project = self._extract_project(query)
        
        # Extract assignee
        slots.assignee = self._extract_assignee(query)
        
        # Extract issuetype
        slots.issuetype = self._extract_issuetype(query)
        
        # Extract status
        slots.status = self._extract_status(query)
        slots.status_category = self._extract_status_category(query)
        
        # Extract priority
        slots.priority = self._extract_priority(query)
        
        # Extract sprint
        slots.sprint = self._extract_sprint(query)
        
        # Extract date range
        slots.date_range = self._extract_date_range(query)
        
        # Extract quantity/top N (only if explicitly mentioned)
        slots.quantity = self._extract_quantity(query)
        
        # Extract order (only if explicitly mentioned)
        slots.order = self._extract_order(query)
        
        # Extract component, label, epic, version (basic patterns)
        slots.component = self._extract_component(query)
        slots.label = self._extract_label(query)
        slots.epic = self._extract_epic(query)
        slots.version = self._extract_version(query)
        slots.fix_version = self._extract_fix_version(query)
        
        return slots

    def _extract_project(self, query: str) -> Optional[SlotValue]:
        """Extract project key from query.
        Rules:
        - Prefer contextual forms: "project = KEY", "project KEY", "KEY project", "in KEY project".
        - Otherwise, only consider 2-5 char tokens that are NOT common nouns (bugs/stories/tasks/etc.).
        """
        q = query.strip()

        # 1) Strong contextual patterns
        ctx_patterns = [
            re.compile(r"\bproject\s*[:=]?\s*([A-Za-z]{2,5})\b", re.IGNORECASE),
            re.compile(r"\bin\s+([A-Za-z]{2,5})\s+project\b", re.IGNORECASE),
            re.compile(r"\b([A-Za-z]{2,5})\s+project\b", re.IGNORECASE)
        ]
        for pat in ctx_patterns:
            m = pat.search(q)
            if m:
                key = m.group(1).upper()
                if key.lower() not in self.common_words and 2 <= len(key) <= 5:
                    # If we have a known project list, ensure the key is one of them
                    if self.known_project_keys and key not in self.known_project_keys:
                        continue
                    return SlotValue(value=key, confidence=0.95, raw_text=key)

        # 2) Token scan with aggressive filtering
        tokens = self.project_pattern.findall(q)
        project_candidates = [t.upper() for t in tokens if t.lower() not in self.common_words]
        # Remove duplicates while preserving order
        seen = set()
        filtered_candidates: List[str] = []
        for candidate in project_candidates:
            cl = candidate.lower()
            if cl in seen:
                continue
            seen.add(cl)
            if cl in self.common_words:
                continue
            filtered_candidates.append(candidate)

        # If we have a known project whitelist, filter candidates to those keys
        if self.known_project_keys and filtered_candidates:
            filtered_candidates = [c for c in filtered_candidates if c in self.known_project_keys]

        if filtered_candidates:
            project_key = filtered_candidates[0]
            if 2 <= len(project_key) <= 5:
                return SlotValue(value=project_key, confidence=0.85, raw_text=project_key)

        return None

    def _extract_assignee(self, query: str) -> Optional[SlotValue]:
        """Extract assignee from query using name patterns"""
        # Look for possessive patterns first (e.g., "ashwin's work")
        possessive_pattern = re.compile(r'\b([A-Z][a-z]+)\'s\b', re.IGNORECASE)
        possessive_match = possessive_pattern.search(query)
        if possessive_match:
            name = possessive_match.group(1)
            return SlotValue(
                value=name,
                confidence=0.95,
                raw_text=f"{name}'s"
            )
        
        # Look for name patterns (capitalized words)
        name_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b')
        matches = name_pattern.findall(query)
        
        # Filter out common words and project keys
        filtered_matches = []
        for match in matches:
            if (match.lower() not in self.common_words and 
                not re.match(r'^[A-Z]{2,5}$', match) and
                len(match.split()) <= 3 and
                match.lower() not in {'work', 'high', 'top', 'did', 'login', 'open', 'show', 'give', 'me', 'get', 'find', 'all', 'the', 'and', 'or', 'for', 'with', 'in', 'on', 'at', 'to', 'from', 'by', 'bugs', 'items', 'ajith'}):
                filtered_matches.append(match)
        
        if filtered_matches:
            return SlotValue(
                value=filtered_matches[0],
                confidence=0.8,
                alternatives=filtered_matches[1:] if len(filtered_matches) > 1 else None,
                raw_text=filtered_matches[0]
            )
        
        return None

    def _extract_issuetype(self, query: str) -> Optional[SlotValue]:
        """Extract issuetype from query"""
        query_lower = query.lower()
        
        for pattern, issuetype in self.issuetype_mappings.items():
            if pattern in query_lower:
                return SlotValue(
                    value=issuetype,
                    confidence=0.9,
                    raw_text=pattern
                )
        
        return None

    def _extract_status(self, query: str) -> Optional[SlotValue]:
        """Extract status from query"""
        query_lower = query.lower()
        
        for pattern, status in self.status_mappings.items():
            if pattern in query_lower:
                return SlotValue(
                    value=status,
                    confidence=0.9,
                    raw_text=pattern
                )
        
        return None

    def _extract_status_category(self, query: str) -> Optional[SlotValue]:
        """Extract status category from query"""
        query_lower = query.lower()
        
        for pattern, category in self.status_category_mappings.items():
            if pattern in query_lower:
                return SlotValue(
                    value=category,
                    confidence=0.9,
                    raw_text=pattern
                )
        
        return None

    def _extract_priority(self, query: str) -> Optional[SlotValue]:
        """Extract priority from query"""
        query_lower = query.lower()
        
        for pattern, priority in self.priority_mappings.items():
            if pattern in query_lower:
                return SlotValue(
                    value=priority,
                    confidence=0.9,
                    raw_text=pattern
                )
        
        return None

    def _extract_sprint(self, query: str) -> Optional[SlotValue]:
        """Extract sprint reference from query"""
        query_lower = query.lower()
        
        # Check for sprint number pattern
        sprint_number_pattern = re.compile(r'sprint\s*#?(\d+)', re.IGNORECASE)
        sprint_match = sprint_number_pattern.search(query)
        if sprint_match:
            sprint_num = sprint_match.group(1)
            return SlotValue(
                value=f"sprint = {sprint_num}",
                confidence=0.95,
                raw_text=f"sprint #{sprint_num}"
            )
        
        # Check for named sprints
        for pattern, sprint_ref in self.sprint_patterns.items():
            if pattern in query_lower:
                return SlotValue(
                    value=sprint_ref,
                    confidence=0.9,
                    raw_text=pattern
                )
        
        return None

    def _extract_date_range(self, query: str) -> Optional[SlotValue]:
        """Extract date range from query"""
        query_lower = query.lower()
        
        for pattern, date_ref in self.date_patterns.items():
            if pattern in query_lower:
                return SlotValue(
                    value=date_ref,
                    confidence=0.9,
                    raw_text=pattern
                )
        
        return None

    def _extract_text_search(self, query: str) -> Optional[SlotValue]:
        """Extract text search terms from query"""
        # Look for quoted text (both single and double quotes)
        quoted_patterns = [
            re.compile(r'"([^"]+)"'),  # Double quotes
            re.compile(r"'([^']+)'")   # Single quotes
        ]
        
        for pattern in quoted_patterns:
            quoted_match = pattern.search(query)
            if quoted_match:
                return SlotValue(
                    value=quoted_match.group(1),
                    confidence=0.95,
                    raw_text=f'"{quoted_match.group(1)}"'
                )
        
        # Look for "contains" or "mentions" patterns
        contains_pattern = re.compile(r'(?:contains?|mentions?)\s+([a-zA-Z0-9\s]+)', re.IGNORECASE)
        contains_match = contains_pattern.search(query)
        if contains_match:
            return SlotValue(
                value=contains_match.group(1).strip(),
                confidence=0.8,
                raw_text=contains_match.group(1).strip()
            )
        
        return None

    def _extract_quantity(self, query: str) -> Optional[SlotValue]:
        """Extract quantity/top N from query"""
        query_lower = query.lower()
        
        # Look for "top N" patterns
        top_pattern = re.compile(r'top\s+(\d+)', re.IGNORECASE)
        top_match = top_pattern.search(query)
        if top_match:
            return SlotValue(
                value=f"TOP {top_match.group(1)}",
                confidence=0.9,
                raw_text=f"top {top_match.group(1)}"
            )
        
        # Look for quantity keywords
        for pattern, quantity in self.quantity_patterns.items():
            if pattern in query_lower:
                return SlotValue(
                    value=quantity,
                    confidence=0.8,
                    raw_text=pattern
                )
        
        return None

    def _extract_order(self, query: str) -> Optional[SlotValue]:
        """Extract order/sort from query"""
        query_lower = query.lower()
        
        for pattern, order in self.order_patterns.items():
            if pattern in query_lower:
                return SlotValue(
                    value=order,
                    confidence=0.9,
                    raw_text=pattern
                )
        
        return None

    def _extract_component(self, query: str) -> Optional[SlotValue]:
        """Extract component from query"""
        component_pattern = re.compile(r'component\s+([a-zA-Z0-9\s]+)', re.IGNORECASE)
        match = component_pattern.search(query)
        if match:
            return SlotValue(
                value=match.group(1).strip(),
                confidence=0.8,
                raw_text=match.group(1).strip()
            )
        return None

    def _extract_label(self, query: str) -> Optional[SlotValue]:
        """Extract label from query"""
        label_pattern = re.compile(r'label\s+([a-zA-Z0-9\s]+)', re.IGNORECASE)
        match = label_pattern.search(query)
        if match:
            return SlotValue(
                value=match.group(1).strip(),
                confidence=0.8,
                raw_text=match.group(1).strip()
            )
        return None

    def _extract_epic(self, query: str) -> Optional[SlotValue]:
        """Extract epic from query"""
        epic_pattern = re.compile(r'epic\s+([a-zA-Z0-9\s\-]+)', re.IGNORECASE)
        match = epic_pattern.search(query)
        if match:
            return SlotValue(
                value=match.group(1).strip(),
                confidence=0.8,
                raw_text=match.group(1).strip()
            )
        return None

    def _extract_version(self, query: str) -> Optional[SlotValue]:
        """Extract version from query"""
        version_pattern = re.compile(r'version\s+([a-zA-Z0-9\.\s\-]+)', re.IGNORECASE)
        match = version_pattern.search(query)
        if match:
            return SlotValue(
                value=match.group(1).strip(),
                confidence=0.8,
                raw_text=match.group(1).strip()
            )
        return None

    def _extract_fix_version(self, query: str) -> Optional[SlotValue]:
        """Extract fix version from query"""
        fix_version_pattern = re.compile(r'fixversion\s+([a-zA-Z0-9\.\s\-]+)', re.IGNORECASE)
        match = fix_version_pattern.search(query)
        if match:
            return SlotValue(
                value=match.group(1).strip(),
                confidence=0.8,
                raw_text=match.group(1).strip()
            )
        return None

    def set_context(self, project: str = None, board: str = None, sprint: str = None):
        """Set context for future queries"""
        if project:
            self.context['project'] = project
        if board:
            self.context['board'] = board
        if sprint:
            self.context['sprint'] = sprint

    def get_context_project(self) -> Optional[str]:
        """Get current project context"""
        return self.context.get('project')

    def set_known_projects(self, project_keys: List[str]):
        """Provide an allowlist of Jira project keys to prefer/limit detection."""
        try:
            # Normalize keys to uppercase and keep short keys only (2-5 chars)
            normalized = [k.upper() for k in project_keys if isinstance(k, str) and 2 <= len(k) <= 5]
            self.known_project_keys = set(normalized)
        except Exception:
            self.known_project_keys = set()

    def compose_jql(self, slots: ExtractedSlots, template: str) -> str:
        """Compose JQL from template using extracted slots"""
        jql = template
        
        # Replace slot placeholders
        replacements = {
            '${PROJECT}': slots.project.value if slots.project else self.get_context_project() or '*',
            '${ASSIGNEE}': slots.assignee.value if slots.assignee else '*',
            '${ISSUETYPE}': slots.issuetype.value if slots.issuetype else '*',
            '${STATUS}': slots.status.value if slots.status else '*',
            '${STATUS_CATEGORY}': slots.status_category.value if slots.status_category else '*',
            '${PRIORITY}': slots.priority.value if slots.priority else '*',
            '${COMPONENT}': slots.component.value if slots.component else '*',
            '${LABEL}': slots.label.value if slots.label else '*',
            '${EPIC}': slots.epic.value if slots.epic else '*',
            '${VERSION}': slots.version.value if slots.version else '*',
            '${FIXVERSION}': slots.fix_version.value if slots.fix_version else '*',
            '${TEXT}': slots.text.value if slots.text else '*',
            '${SPRINT_SCOPE}': slots.sprint.value if slots.sprint else 'openSprints()',
            '${START}': slots.date_range.value if slots.date_range else '*',
            '${END}': 'now()',
            '${ORDER}': slots.order.value if slots.order else 'updated DESC',
            '${DAYS}': '7'  # Default for inactive queries
        }
        
        # Apply replacements
        for placeholder, value in replacements.items():
            if placeholder in jql:
                if value == '*':
                    # Remove the entire clause if no value
                    jql = self._remove_clause(jql, placeholder)
                else:
                    jql = jql.replace(placeholder, str(value))
        
        # Clean up JQL
        jql = self._clean_jql(jql)
        
        return jql

    def _remove_clause(self, jql: str, placeholder: str) -> str:
        """Remove JQL clause containing placeholder"""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated clause removal
        lines = jql.split('\n')
        cleaned_lines = []
        for line in lines:
            if placeholder not in line:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    def _clean_jql(self, jql: str) -> str:
        """Clean up JQL by removing empty clauses and fixing syntax"""
        # Remove multiple spaces
        jql = re.sub(r'\s+', ' ', jql)
        
        # Remove empty AND/OR clauses
        jql = re.sub(r'\s+AND\s+$', '', jql)
        jql = re.sub(r'\s+OR\s+$', '', jql)
        
        # Fix multiple AND/OR
        jql = re.sub(r'\s+AND\s+AND\s+', ' AND ', jql)
        jql = re.sub(r'\s+OR\s+OR\s+', ' OR ', jql)
        
        return jql.strip()
