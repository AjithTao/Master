import json
import os
import re
from typing import Optional, Dict, Any, List
from rapidfuzz import process, fuzz
from utils.slot_based_nlu import SlotBasedNLU, ExtractedSlots

class EnhancedJQLTrainingLoader:
    """Enhanced training loader with slot-based template support"""
    
    def __init__(self, training_file: str):
        if not os.path.exists(training_file):
            raise FileNotFoundError(f"Training file not found: {training_file}")
        
        with open(training_file, "r", encoding="utf-8") as f:
            self.training_data: List[Dict[str, Any]] = json.load(f)
        
        # Initialize slot-based NLU
        self.slot_nlu = SlotBasedNLU()
        
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
                self._map[key] = {
                    "intent": intent, 
                    "jql": jql, 
                    "template": expected,
                    "is_template": "${" in jql  # Check if this is a template
                }

    def find(self, user_query: str, cutoff: float = 0.88) -> Optional[Dict[str, Any]]:
        """Find best match with slot-based template support.
        Slot-aware gating: if an assignee/project/issuetype is clearly present,
        avoid returning a generic template that ignores those slots so the
        downstream advanced generator can handle it precisely.
        """
        if not user_query:
            return None
        
        q = user_query.strip().lower()
        # Extract slots early for gating
        slots = self.slot_nlu.extract_slots(user_query)
        
        # First try exact match
        if q in self._map:
            match = self._map[q]
            # Guard against generic intents hijacking slot-rich queries
            if self._should_reject_match_due_to_slots(match, slots):
                return None
            if match["is_template"]:
                return self._process_template_match(match, user_query)
            return match
        
        # Fuzzy matching
        match = process.extractOne(
            q,
            self._questions,
            scorer=fuzz.token_set_ratio,
            score_cutoff=int(cutoff * 100)
        )
        
        if not match:
            return None
        
        best_q, score, _ = match
        match_data = self._map.get(best_q)
        
        if match_data:
            if self._should_reject_match_due_to_slots(match_data, slots):
                return None
            if match_data["is_template"]:
                return self._process_template_match(match_data, user_query)
        
        return match_data

    def _should_reject_match_due_to_slots(self, match: Dict[str, Any], slots: ExtractedSlots) -> bool:
        """Reject generic matches when specific slots are present.
        Examples:
        - If an assignee is present but the matched JQL has no assignee, reject.
        - If issuetype is present but the matched JQL has no issuetype placeholder/clause, reject.
        - If a project is present but the matched JQL has no project placeholder/clause, reject.
        """
        try:
            jql = match.get("jql", "") or ""
            jql_lower = jql.lower()
            if slots.assignee and ("assignee" not in jql_lower and "${assignee}" not in jql_lower):
                return True
            if slots.issuetype and ("issuetype" not in jql_lower and "${issuetype}" not in jql_lower):
                return True
            if slots.project and ("project" not in jql_lower and "${project}" not in jql_lower):
                return True
        except Exception:
            return False
        return False

    def _process_template_match(self, match: Dict[str, Any], user_query: str) -> Optional[Dict[str, Any]]:
        """Process template match by extracting slots and composing JQL"""
        try:
            # Extract slots from user query
            slots = self.slot_nlu.extract_slots(user_query)
            
            # Compose JQL from template
            composed_jql = self.slot_nlu.compose_jql(slots, match["jql"])
            
            # Compose response template
            composed_response = self._compose_response(match["template"], slots)
            
            return {
                "intent": match["intent"],
                "jql": composed_jql,
                "template": composed_response,
                "is_template": False,  # Now it's a concrete JQL
                "slots_used": self._get_used_slots(slots)
            }
            
        except Exception as e:
            print(f"Error processing template match: {e}")
            return None

    def _compose_response(self, template: str, slots: ExtractedSlots) -> str:
        """Compose response template with slot values"""
        response = template
        
        # Replace slot placeholders in response
        replacements = {
            '${PROJECT}': slots.project.value if slots.project else 'the project',
            '${ASSIGNEE}': slots.assignee.value if slots.assignee else 'the assignee',
            '${ISSUETYPE}': slots.issuetype.value if slots.issuetype else 'items',
            '${STATUS}': slots.status.value if slots.status else 'items',
            '${STATUS_CATEGORY}': slots.status_category.value if slots.status_category else 'items',
            '${PRIORITY}': slots.priority.value if slots.priority else 'items',
            '${COMPONENT}': slots.component.value if slots.component else 'the component',
            '${LABEL}': slots.label.value if slots.label else 'the label',
            '${EPIC}': slots.epic.value if slots.epic else 'the epic',
            '${VERSION}': slots.version.value if slots.version else 'the version',
            '${TEXT}': slots.text.value if slots.text else 'the text',
            '${DAYS}': '7'  # Default for inactive queries
        }
        
        for placeholder, value in replacements.items():
            if placeholder in response:
                response = response.replace(placeholder, str(value))
        
        return response

    def _get_used_slots(self, slots: ExtractedSlots) -> Dict[str, str]:
        """Get dictionary of used slots"""
        used_slots = {}
        
        if slots.project:
            used_slots['project'] = slots.project.value
        if slots.assignee:
            used_slots['assignee'] = slots.assignee.value
        if slots.issuetype:
            used_slots['issuetype'] = slots.issuetype.value
        if slots.status:
            used_slots['status'] = slots.status.value
        if slots.status_category:
            used_slots['status_category'] = slots.status_category.value
        if slots.priority:
            used_slots['priority'] = slots.priority.value
        if slots.component:
            used_slots['component'] = slots.component.value
        if slots.label:
            used_slots['label'] = slots.label.value
        if slots.epic:
            used_slots['epic'] = slots.epic.value
        if slots.version:
            used_slots['version'] = slots.version.value
        if slots.text:
            used_slots['text'] = slots.text.value
        if slots.sprint:
            used_slots['sprint'] = slots.sprint.value
        if slots.date_range:
            used_slots['date_range'] = slots.date_range.value
        if slots.order:
            used_slots['order'] = slots.order.value
        if slots.quantity:
            used_slots['quantity'] = slots.quantity.value
        
        return used_slots

    def set_context(self, project: str = None, board: str = None, sprint: str = None):
        """Set context for future queries"""
        self.slot_nlu.set_context(project, board, sprint)

    def get_context_project(self) -> Optional[str]:
        """Get current project context"""
        return self.slot_nlu.get_context_project()
