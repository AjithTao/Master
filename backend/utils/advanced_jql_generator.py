"""
Advanced JQL Generation Logic
Handles multiple matches, full name handling, fuzzy matching, and project detection
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from rapidfuzz import process, fuzz
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NameMatch:
    """Represents a name match result"""
    original_name: str
    matched_name: str
    similarity_score: float
    account_id: Optional[str] = None

@dataclass
class JQLResult:
    """Represents a JQL query result"""
    jql: str
    count: int
    issues: List[Dict[str, Any]]
    success: bool
    error_message: Optional[str] = None

class AdvancedJQLGenerator:
    """Advanced JQL generator with improved name handling and matching"""
    
    def __init__(self, jira_client, project_ctx: str = None):
        self.jira_client = jira_client
        self.project_ctx = project_ctx
        self.known_assignees = set()
        self.assignee_cache = {}
        self._project_keys_cache = None
        
        # Alias dictionary for known name variations
        self.name_aliases = {
            'ashwini': 'Ashwini Kumar',
            'ashwin': 'Ashwin Thyagarajan',
            'ashwini kumar': 'Ashwini Kumar',
            'ashwin thyag': 'Ashwin Thyagarajan',
            'thyagarajan': 'Ashwin Thyagarajan',
            'saiteja': 'Sai Teja Miriyala',
            'sai teja': 'Sai Teja Miriyala',
            'srikanth': 'Srikanth Chitturi',
            'karthikeya': 'Karthikeya',
            'ajith': 'Ajith Kumar',
            'ajith kumar': 'Ajith Kumar',
            'priya': 'Priya Sharma',
            'priya sharma': 'Priya Sharma'
        }
        
        # More specific project pattern - avoid common words
        self.project_token = re.compile(r'\b([A-Z]{2,5})\b', re.IGNORECASE)
    
    async def _valid_project_keys(self) -> set[str]:
        """Get valid project keys from Jira"""
        if self._project_keys_cache is None:
            try:
                keys = await self.jira_client.get_project_keys()
                self._project_keys_cache = set(keys or [])
            except Exception as e:
                logger.error(f"Error getting project keys: {e}")
                self._project_keys_cache = set()
        return self._project_keys_cache

    def _strip_possessive(self, s: str) -> str:
        """Strip possessive 's from names: 'ashwin's' -> 'ashwin'"""
        return re.sub(r"'s\b", "", s.strip().lower())

    async def generate_jql(self, query: str) -> Dict[str, Any]:
        """Generate JQL for queries with advanced matching - handles both assignee and project queries"""
        try:
            q = query.strip()
            logger.debug(f"generate_jql received query: {q}")
            
            # 1) Project first (more permissive - don't require validation)
            tokens = [t for t in self.project_token.findall(q)]
            logger.debug(f"candidate project tokens: {tokens}")
            
            # Filter out common words that aren't project keys
            common_words = {
                'give','me','show','get','find','open','closed','all','the','and','or','for','with','in','on','at','to','from','by',
                'bug','bugs','defect','defects','issue','issues','ticket','tickets','item','items','story','stories','task','tasks','project','projects',
                'list'  # explicitly exclude to avoid false positives
            }
            project_candidates = [t.upper() for t in tokens if t.lower() not in common_words]
            
            if project_candidates:
                valid_keys = await self._valid_project_keys()
                # Only keep tokens that are REAL project keys
                filtered = [k for k in project_candidates if k in valid_keys]
                logger.debug(f"validated project candidates: {filtered}")
                if filtered:
                    # Prefer contextual cues if present
                    contextual = None
                    ctx_patterns = [
                        re.compile(r"\bproject\s*[:=]?\s*([A-Za-z]{2,5})\b", re.IGNORECASE),
                        re.compile(r"\bin\s+([A-Za-z]{2,5})\s+project\b", re.IGNORECASE),
                        re.compile(r"\b([A-Za-z]{2,5})\s+project\b", re.IGNORECASE)
                    ]
                    for pat in ctx_patterns:
                        m = pat.search(q)
                        if m:
                            key = m.group(1).upper()
                            if key in filtered:
                                contextual = key
                                break
                    project_key = contextual or filtered[0]
                    if len(project_key) >= 2 and len(project_key) <= 5:
                        return await self.generate_project_jql(q, [project_key])
            
            # 2) Assignee/name path
            extracted = self._extract_names_relaxed(q)
            logger.debug(f"extracted names: {extracted}")
            if not extracted:
                return {
                    "success": False,
                    "error": "no_names_or_projects",
                    "response": "Tell me a project (e.g., CCM) or a person (e.g., Ashwin)."
                }
            
            if len(extracted) > 1:
                return await self._handle_multiple_names(extracted, q)
            
            name = extracted[0]
            return await self._process_single_name(name, q)
            
        except Exception as e:
            logger.error(f"Error in generate_jql: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"Sorry, I encountered an error while processing your query: {str(e)}"
            }
    
    async def generate_assignee_jql(self, query: str) -> Dict[str, Any]:
        """Generate JQL for assignee-based queries with advanced matching"""
        return await self.generate_jql(query)
    
    def _extract_names_relaxed(self, query: str) -> List[str]:
        """
        Accept lowercase names, handle possessives, and consult alias map.
        """
        words = re.findall(r"[A-Za-z']+", query)
        names = []
        buff = []

        skip = {
            'worked','assigned','assignee','who','is','has','on','to','the','a','an','show','me',
            'tickets','what','working','does','have','tell','about','give','list','all','find',
            'search','for','tasks','stories','bugs','issues','items','work','done','progress',
            'current','sprint','open','closed','in','project'
        }

        for raw in words:
            w = self._strip_possessive(raw)
            if not w or w in skip:
                if buff: 
                    names.append(" ".join(buff))
                    buff = []
                continue
            
            # Alias direct hit (handles lowercase singletons like 'ashwini')
            if w in self.name_aliases:
                if buff: 
                    names.append(" ".join(buff))
                    buff = []
                names.append(self.name_aliases[w])
                continue
            
            # Keep capitalized sequences as names too
            if raw and raw[0].isupper():
                buff.append(raw)
            else:
                if buff: 
                    names.append(" ".join(buff))
                    buff = []

        if buff: 
            names.append(" ".join(buff))
        
        # Normalize single lowercase tokens that might be names
        out = []
        for n in names:
            nn = n.strip()
            if not nn: 
                continue
            low = nn.lower()
            out.append(self.name_aliases.get(low, nn))
        
        # Deduplicate while preserving order (case-insensitive)
        seen_lower = set()
        deduped: List[str] = []
        for val in out:
            key = val.lower()
            if key in seen_lower:
                continue
            seen_lower.add(key)
            deduped.append(val)
        
        return [x for x in deduped if x]

    async def _find_name_matches(self, name: str) -> List[NameMatch]:
        """Aggregate exact, partial, fuzzy and alias matches into a uniform list."""
        results: List[NameMatch] = []
        try:
            # exact
            exact = await self._find_exact_jira_user(name)
            if exact:
                results.append(NameMatch(original_name=name, matched_name=exact, similarity_score=100.0))
                return results
            # partials
            partials = await self._find_partial_jira_users(name)
            for user in partials:
                dn = user.get('displayName')
                if dn:
                    results.append(NameMatch(original_name=name, matched_name=dn, similarity_score=90.0, account_id=user.get('accountId')))
            # fuzzy
            fuzzy = await self._find_fuzzy_matches(name)
            results.extend(fuzzy)
            # alias as last resort
            alias = self._check_alias_dictionary(name)
            if alias:
                results.append(NameMatch(original_name=name, matched_name=alias, similarity_score=85.0))
        except Exception as e:
            logger.error(f"_find_name_matches error for '{name}': {e}")
        return results
    
    async def _handle_multiple_names(self, names: List[str], query: str) -> Dict[str, Any]:
        """Handle queries with multiple names"""
        # Normalize and deduplicate inputs first
        unique_inputs = []
        seen = set()
        for n in names:
            k = n.strip()
            if not k:
                continue
            kl = k.lower()
            if kl in seen:
                continue
            seen.add(kl)
            unique_inputs.append(k)

        # If duplicates collapsed to a single person, treat it as single-name flow
        if len(unique_inputs) == 1:
            return await self._process_single_name(unique_inputs[0], query)

        # Otherwise, try to resolve each uniquely
        matched_names = []
        for name in unique_inputs:
            matches = await self._find_name_matches(name)
            if matches:
                matched_names.extend(matches)
        
        if len(matched_names) > 1:
            # Multiple matches found - ask for clarification
            unique_names = list(set([match.matched_name for match in matched_names]))
            return {
                'success': False,
                'error': 'multiple_matches',
                'response': self._format_multiple_matches_response(unique_names, query)
            }
        elif len(matched_names) == 1:
            # Single match found - proceed with that
            return await self._process_single_name(matched_names[0].matched_name, query)
        else:
            # No matches found - if alias resolves uniquely, try that; else inform user
            alias_resolved = []
            for n in unique_inputs:
                a = self._check_alias_dictionary(n)
                alias_resolved.append(a or n)
            alias_unique = list({x.lower(): x for x in alias_resolved}.values())
            if len(alias_unique) == 1:
                return await self._process_single_name(alias_unique[0], query)
            return {
                'success': False,
                'error': 'no_matches',
                'response': f"I couldn't find any tickets for the names mentioned: {', '.join(unique_inputs)}. Please check the spelling or try a different name."
            }
    
    async def _process_single_name(self, name: str, query: str) -> Dict[str, Any]:
        """Process a single name with exact matching priority"""
        try:
            # Step 1: Exact Jira user match
            exact_match = await self._find_exact_jira_user(name)
            if exact_match:
                logger.info(f"Exact match found: {exact_match}")
                return await self._generate_assignee_jql_with_validation(exact_match, query)
            
            # Step 2: Partial Jira user match
            partial_matches = await self._find_partial_jira_users(name)
            if len(partial_matches) > 1:
                # Multiple partial matches - ask for clarification
                unique_names = list(set([match['displayName'] for match in partial_matches]))
                return {
                    'success': False,
                    'error': 'multiple_partial_matches',
                    'response': self._format_multiple_matches_response(unique_names, query)
                }
            elif len(partial_matches) == 1:
                # Single partial match - use it
                logger.info(f"Partial match found: {partial_matches[0]['displayName']}")
                return await self._generate_assignee_jql_with_validation(partial_matches[0]['displayName'], query)
            
            # Step 3: Fuzzy matching (only if no exact or partial matches)
            fuzzy_matches = await self._find_fuzzy_matches(name)
            if len(fuzzy_matches) > 1:
                # Multiple fuzzy matches - ask for clarification
                unique_names = list(set([match.matched_name for match in fuzzy_matches]))
                return {
                    'success': False,
                    'error': 'multiple_fuzzy_matches',
                    'response': self._format_multiple_matches_response(unique_names, query)
                }
            elif len(fuzzy_matches) == 1:
                # Single fuzzy match - use it
                logger.info(f"Fuzzy match found: {fuzzy_matches[0].matched_name}")
                return await self._generate_assignee_jql_with_validation(fuzzy_matches[0].matched_name, query)
            
            # Step 4: Alias dictionary (only if no other matches)
            alias_match = self._check_alias_dictionary(name)
            if alias_match:
                logger.info(f"Alias match found: {alias_match}")
                return await self._generate_assignee_jql_with_validation(alias_match, query)
            
            # Step 5: Last-resort fallback – try generating JQL directly with provided name.
            # This leverages accountId resolution under the hood and name-based contains (~) match.
            try:
                logger.info(f"No exact/partial/fuzzy/alias match. Attempting direct JQL with provided name: {name}")
                direct = await self._generate_assignee_jql_with_validation(name, query)
                if direct.get('success'):
                    return direct
            except Exception:
                pass

            # Still no matches
            return {
                'success': False,
                'error': 'no_matches',
                'response': f"I couldn't find any tickets for '{name}'. Please check the spelling or try a different name."
            }
            
        except Exception as e:
            logger.error(f"Error in _process_single_name: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"Sorry, I encountered an error while processing '{name}': {str(e)}"
            }
    
    async def _find_exact_jira_user(self, name: str) -> Optional[str]:
        """Find exact match in Jira users"""
        try:
            # Get all Jira users
            users = await self._get_all_jira_users()
            
            # Check for exact match (case-insensitive)
            name_lower = name.lower().strip()
            for user in users:
                display_name = user.get('displayName', '')
                if display_name.lower() == name_lower:
                    return display_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error in _find_exact_jira_user: {e}")
            return None
    
    async def _find_partial_jira_users(self, name: str) -> List[Dict[str, Any]]:
        """Find Jira users whose names contain the given string"""
        try:
            # Get all Jira users
            users = await self._get_all_jira_users()
            
            partial_matches = []
            name_lower = name.lower().strip()
            
            for user in users:
                display_name = user.get('displayName', '')
                if name_lower in display_name.lower():
                    partial_matches.append(user)
            
            return partial_matches
            
        except Exception as e:
            logger.error(f"Error in _find_partial_jira_users: {e}")
            return []
    
    async def _get_all_jira_users(self) -> List[Dict[str, Any]]:
        """Get all Jira users from the system"""
        if hasattr(self, '_jira_users_cache') and self._jira_users_cache:
            return self._jira_users_cache
        
        try:
            # Use Jira's user search API to get all users
            # This is more comprehensive than getting users from issues
            users = []
            
            # Try to get users from recent issues first (fallback method)
            jql = "updated >= -30d ORDER BY updated DESC"
            result = await self.jira_client.search(jql, max_results=1000)
            
            user_set = set()
            for issue in result.get('issues', []):
                # Get assignee
                assignee = issue.get('fields', {}).get('assignee')
                if assignee and assignee.get('displayName'):
                    user_key = assignee.get('displayName')
                    if user_key not in user_set:
                        user_set.add(user_key)
                        users.append({
                            'displayName': assignee.get('displayName'),
                            'accountId': assignee.get('accountId'),
                            'emailAddress': assignee.get('emailAddress')
                        })
                
                # Get reporter
                reporter = issue.get('fields', {}).get('reporter')
                if reporter and reporter.get('displayName'):
                    user_key = reporter.get('displayName')
                    if user_key not in user_set:
                        user_set.add(user_key)
                        users.append({
                            'displayName': reporter.get('displayName'),
                            'accountId': reporter.get('accountId'),
                            'emailAddress': reporter.get('emailAddress')
                        })
            
            # Cache the results
            self._jira_users_cache = users
            return users
            
        except Exception as e:
            logger.error(f"Error getting Jira users: {e}")
            return []
    
    def _check_alias_dictionary(self, name: str) -> Optional[str]:
        """Check alias dictionary for known name variations"""
        normalized_name = name.lower().strip()
        return self.name_aliases.get(normalized_name)
    
    async def _find_fuzzy_matches(self, name: str) -> List[NameMatch]:
        """Find name matches using fuzzy matching against Jira users"""
        try:
            # Get all Jira users
            users = await self._get_all_jira_users()
            
            if not users:
                return []
            
            # Perform fuzzy matching
            matches = []
            for user in users:
                display_name = user.get('displayName', '')
                similarity = fuzz.ratio(name.lower(), display_name.lower())
                if similarity >= 80:  # 80% similarity threshold
                    matches.append(NameMatch(
                        original_name=name,
                        matched_name=display_name,
                        similarity_score=similarity,
                        account_id=user.get('accountId')
                    ))
            
            # Sort by similarity score (highest first)
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            return matches
            
        except Exception as e:
            logger.error(f"Error in _find_fuzzy_matches: {e}")
            return []
    
    async def _generate_assignee_jql_with_validation(self, assignee_name: str, query: str) -> Dict[str, Any]:
        """Generate JQL for assignee with validation"""
        try:
            # Prefer accountId based query if we can resolve the user
            try:
                base_assignee_clause = await self.jira_client.build_assignee_jql(assignee_name)
            except Exception:
                base_assignee_clause = None

            if base_assignee_clause and 'assignee in (' in base_assignee_clause:
                # We have a precise accountId; start with only this variant
                base = [base_assignee_clause]
            else:
                # Fallback to name-based variants
                sanitized = assignee_name.replace('"', '\\"')
                base = [
                    f'assignee = "{sanitized}"',
                    f'assignee ~ "{sanitized}"',
                    f'assignee in ("{sanitized}")'
                ]

            # Issuetype hint
            ql = query.lower()
            if 'story' in ql or 'stories' in ql:
                base = [f"{b} AND issuetype = Story" for b in base]
            elif 'bug' in ql or 'defect' in ql or 'bugs' in ql or 'defects' in ql:
                base = [f"{b} AND issuetype in (Bug, Defect)" for b in base]
            elif 'task' in ql or 'tasks' in ql:
                base = [f"{b} AND issuetype = Task" for b in base]

            # Status category hint (open vs done)
            if 'statuscategory' not in ql:
                if 'open' in ql or 'in progress' in ql or 'progress' in ql:
                    base = [f"{b} AND statusCategory != Done" for b in base]
                elif 'closed' in ql or 'done' in ql or 'completed' in ql:
                    base = [f"{b} AND statusCategory = Done" for b in base]

            # Project context - extract project from query if mentioned
            project_hint = None
            ql = query.lower()
            
            # Direct project mentions
            if 'ccm' in ql:
                project_hint = 'CCM'
            elif 'crm' in ql:
                project_hint = 'CRM'
            elif 'project' in ql:
                # Extract project key from query
                import re
                project_match = re.search(r'\b([A-Z]{2,5})\b', query)
                if project_match:
                    project_hint = project_match.group(1)
            
            # Don't assume project - let the workaround try all projects if needed
            # The workaround will handle project detection from the JQL
            
            if project_hint:
                base = [f'project = {project_hint} AND {b}' for b in base]
                logger.debug(f"Added project filter: {project_hint}")
            elif self.project_ctx:
                base = [f'project = {self.project_ctx} AND {b}' for b in base]
                logger.debug(f"Using project context: {self.project_ctx}")
            
            logger.debug(f"Final JQL variants: {base}")

            for jql in base:
                try:
                    total = await self.jira_client.count(jql)
                    logger.debug(f"Count for JQL '{jql}': {total}")
                    if total > 0:
                        # Fetch examples with explicit fields
                        fields = ["id", "key", "summary", "status", "issuetype", "assignee", "project", "created", "updated"]
                        sr = await self.jira_client.search(jql, max_results=10, fields=fields)
                        issues_raw = sr.get('issues', [])
                        logger.debug(f"Raw issues fetched: {len(issues_raw)}")
                        
                        # The search method now handles workarounds internally
                        if not issues_raw and total > 0:
                            logger.debug("No issues from search workaround, but count > 0. This may be due to API limitations.")
                        
                        # Validate assignee results
                        issues = self._validate_assignee_results(issues_raw, assignee_name)
                        logger.debug(f"After validation: {len(issues)} issues")
                        
                        # If validation filtered everything but we have raw issues, use them
                        if not issues and issues_raw:
                            logger.debug("Using raw issues due to validation filtering")
                            issues = issues_raw
                        
                        return {
                            "success": True,
                            "jql": jql,
                            "count": total,
                            "issues": issues,
                            "assignee_name": assignee_name,
                            "response": self._format_assignee_response(assignee_name, total, issues)
                        }
                except Exception as e:
                    logger.error(f"JQL failed: {jql} -> {e}")
                    continue

            return {
                "success": False,
                "error": "no_results",
                "response": f"I found '{assignee_name}' in the system but couldn't find any tickets assigned to them."
            }
            
        except Exception as e:
            logger.error(f"Error in _generate_assignee_jql_with_validation: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"Sorry, I encountered an error while searching for {assignee_name}: {str(e)}"
            }
    
    def _validate_assignee_results(self, issues: List[Dict[str, Any]], assignee_name: str) -> List[Dict[str, Any]]:
        """Validate that returned issues actually belong to the queried assignee"""
        validated_issues = []
        
        for issue in issues:
            issue_assignee = issue.get('fields', {}).get('assignee', {}).get('displayName', '')
            if issue_assignee and (
                issue_assignee.lower() == assignee_name.lower() or
                assignee_name.lower() in issue_assignee.lower() or
                issue_assignee.lower() in assignee_name.lower()
            ):
                validated_issues.append(issue)
            else:
                logger.warning(f"Filtering out ticket {issue.get('key')} - assignee '{issue_assignee}' doesn't match queried '{assignee_name}'")
        
        return validated_issues
    
    def _format_multiple_matches_response(self, names: List[str], query: str) -> str:
        """Format response for multiple name matches"""
        if len(names) == 2:
            return f"🤔 I found multiple people matching your query:\n• {names[0]}\n• {names[1]}\n\nPlease tell me which one you meant."
        else:
            name_list = '\n• '.join(names)
            return f"🤔 I found multiple people matching your query:\n• {name_list}\n\nPlease tell me which one you meant."
    
    def _format_assignee_response(self, assignee_name: str, count: int, issues: List[Dict[str, Any]]) -> str:
        """Engaging response for assignee queries with neat breakdown and examples"""
        logger.debug(f"Formatting response for {assignee_name}: count={count}, issues={len(issues)}")
        
        if count == 0:
            return f"I can see {assignee_name} in Jira, but there are no tickets currently assigned to them."

        # Group by status
        status_groups: Dict[str, List[Dict[str, Any]]] = {}
        for issue in issues:
            status = issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
            status_groups.setdefault(status, []).append(issue)
            logger.debug(f"Issue {issue.get('key', 'UNKNOWN')}: status={status}")

        logger.debug(f"Status groups: {dict((k, len(v)) for k, v in status_groups.items())}")

        # Header
        header = f"{assignee_name}: {count} ticket{'s' if count != 1 else ''}"

        # Breakdown
        breakdown_lines: List[str] = []
        for status, items in sorted(status_groups.items(), key=lambda kv: kv[0]):
            breakdown_lines.append(f"- {status}: {len(items)}")

        # Examples (top 3 by updated if available)
        def _ex_line(issue: Dict[str, Any]) -> str:
            key = issue.get('key', 'UNKNOWN')
            fields = issue.get('fields', {})
            summary = (fields.get('summary') or 'No summary').strip()
            status = fields.get('status', {}).get('name', 'Unknown')
            return f"- {key}: {summary} ({status})"

        try:
            sorted_all = sorted(issues, key=lambda i: (i.get('fields', {}).get('updated') or ''), reverse=True)
        except Exception:
            sorted_all = issues
        example_lines = [_ex_line(i) for i in sorted_all[:3]]

        parts: List[str] = [header, "", "Status breakdown:"]
        parts.extend(breakdown_lines)
        if example_lines:
            parts.extend(["", "Recent examples:"])
            parts.extend(example_lines)
        
        result = '\n'.join(parts)
        logger.debug(f"Formatted response: {result}")
        return result
    
    async def generate_project_jql(self, query: str, project_keys: List[str] = None) -> Dict[str, Any]:
        """Generate JQL for project-based queries"""
        try:
            if not project_keys:
                # Extract project keys from query
                tokens = [t for t in self.project_token.findall(query)]
                valid_projects = await self._valid_project_keys()
                project_keys = [t.upper() for t in tokens if t.upper() in valid_projects]
            
            if not project_keys:
                return {
                    'success': False,
                    'error': 'no_project_keys',
                    'response': "I couldn't find any valid project keys in your query. Please specify a project like CCM, CRM, etc."
                }
            
            # Handle multiple project keys
            if len(project_keys) > 1:
                return await self._handle_multiple_projects(project_keys, query)
            
            # Single project processing
            project_key = project_keys[0]
            return await self._process_single_project(project_key, query)
            
        except Exception as e:
            logger.error(f"Error in generate_project_jql: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"Sorry, I encountered an error while processing your project query: {str(e)}"
            }
    
    async def _handle_multiple_projects(self, project_keys: List[str], query: str) -> Dict[str, Any]:
        """Handle queries with multiple project keys"""
        # Generate JQL for multiple projects
        project_conditions = [f'project = "{key}"' for key in project_keys]
        jql = f'({" OR ".join(project_conditions)}) ORDER BY updated DESC'
        
        try:
            result = await self.jira_client.search(jql, max_results=100)
            count = result.get('total', 0)
            
            if count > 0:
                return {
                    'success': True,
                    'jql': jql,
                    'count': count,
                    'issues': result['issues'],
                    'project_keys': project_keys,
                    'response': f"Found {count} tickets across projects: {', '.join(project_keys)}"
                }
            else:
                return {
                    'success': False,
                    'error': 'no_results',
                    'response': f"I couldn't find any tickets in projects: {', '.join(project_keys)}"
                }
                
        except Exception as e:
            logger.error(f"Error in _handle_multiple_projects: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"Sorry, I encountered an error while searching projects: {str(e)}"
            }
    
    async def _process_single_project(self, project_key: str, query: str) -> Dict[str, Any]:
        """Process a single project with fallback queries"""
        # Start with basic project query (without quotes)
        base_jql = f'project = {project_key}'
        
        # Try the basic query first
        primary_jql = f'{base_jql} ORDER BY updated DESC'
        
        try:
            total = await self.jira_client.count(primary_jql)
            
            if total > 0:
                # Fetch some examples
                sr = await self.jira_client.search(primary_jql, max_results=10)
                issues = sr.get('issues', [])
                response = self._format_project_response(project_key, total, issues, query)
                return {
                    'success': True,
                    'jql': primary_jql,
                    'count': total,
                    'issues': issues,
                    'project_key': project_key,
                    'response': response
                }
            
            # Try fallback queries
            fallback_jqls = [
                f'text ~ "{project_key}" ORDER BY updated DESC',
                f'summary ~ "{project_key}" ORDER BY updated DESC'
            ]
            
            for fallback_jql in fallback_jqls:
                try:
                    fallback_total = await self.jira_client.count(fallback_jql)
                    
                    if fallback_total > 0:
                        sr = await self.jira_client.search(fallback_jql, max_results=10)
                        issues = sr.get('issues', [])
                        response = self._format_project_response(project_key, fallback_total, issues, query)
                        return {
                            'success': True,
                            'jql': fallback_jql,
                            'count': fallback_total,
                            'issues': issues,
                            'project_key': project_key,
                            'response': response
                        }
                
                except Exception as e:
                    logger.error(f"Fallback JQL failed: {fallback_jql}, Error: {e}")
                    continue
            
            # No results found
            return {
                'success': False,
                'error': 'no_results',
                'response': f"I couldn't find any tickets for project '{project_key}'. Please check if the project key is correct."
            }
            
        except Exception as e:
            logger.error(f"Error in _process_single_project: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"Sorry, I encountered an error while searching project '{project_key}': {str(e)}"
            }

    def _format_project_response(self, project_key: str, count: int, issues: List[Dict[str, Any]], kind_hint: str = "") -> str:
        """Create an engaging project-level response with a few examples."""
        hint = (kind_hint or "").lower()
        header = f"{project_key}: {count} item{'s' if count != 1 else ''}"
        if not issues:
            return header

        lines: List[str] = [header, "", "Recent examples:"]
        for issue in issues[:3]:
            key = issue.get('key', 'UNKNOWN')
            fields = issue.get('fields', {})
            summary = (fields.get('summary') or 'No summary').strip()
            status = fields.get('status', {}).get('name', 'Unknown')
            lines.append(f"- {key}: {summary} ({status})")
        return '\n'.join(lines)

