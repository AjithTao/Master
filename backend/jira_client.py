from __future__ import annotations
import httpx
import asyncio
from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote
from datetime import datetime, timedelta
from auth import JiraConfig
import json
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class JiraClient:
    cfg: JiraConfig
    _client: Optional[httpx.AsyncClient] = None
    _sprint_field_id: Optional[str] = None
    _field_cache: Optional[Dict[str, Any]] = None
    _assignee_cache: Optional[Dict[str, str]] = None
    _project_cache: Optional[Dict[str, Any]] = None
    _cache_timestamp: Optional[datetime] = None
    _intent_templates: Optional[List[Dict[str, Any]]] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            auth=(self.cfg.email, self.cfg.api_token),
            timeout=httpx.Timeout(60.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        await self._initialize_caches()
        self._load_intent_templates()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()

    async def initialize(self):
        """Initialize the client for persistent use"""
        if not self._client:
            self._client = httpx.AsyncClient(
                auth=(self.cfg.email, self.cfg.api_token),
                timeout=httpx.Timeout(60.0),
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
            await self._initialize_caches()
            self._load_intent_templates()

    async def close(self):
        """Close the client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _initialize_caches(self):
        """Initialize all caches including fields, assignees, and projects"""
        try:
            # Initialize field cache
            await self._cache_fields()
            
            # Initialize assignee cache
            await self._cache_assignees()
            
            # Initialize project cache
            await self._cache_projects()
            
            self._cache_timestamp = datetime.now()
            logger.info("Successfully initialized all caches")
            
        except Exception as e:
            logger.error(f"Failed to initialize caches: {e}")
            # Fallback to basic sprint field discovery
            await self._discover_sprint_field_fallback()

    def _load_intent_templates(self) -> None:
        """Load base and custom JQL intent templates from backend/data."""
        try:
            base_path = os.path.join(os.path.dirname(__file__), 'data', 'jira_intents.json')
            custom_path = os.path.join(os.path.dirname(__file__), 'data', 'custom_jira_intents.json')
            templates: List[Dict[str, Any]] = []
            if os.path.exists(base_path):
                with open(base_path, 'r', encoding='utf-8') as f:
                    templates.extend(json.load(f))
            if os.path.exists(custom_path):
                with open(custom_path, 'r', encoding='utf-8') as f:
                    templates.extend(json.load(f))
            # Deduplicate by id if present
            dedup: Dict[str, Dict[str, Any]] = {}
            for t in templates:
                tid = t.get('id') or f"{t.get('intent','unknown')}::{t.get('jql','')}"
                dedup[tid] = t
            self._intent_templates = list(dedup.values())
            logger.info(f"Loaded {len(self._intent_templates)} intent templates for JQL generation")
        except Exception as e:
            logger.warning(f"Failed to load intent templates: {e}")
            self._intent_templates = []

    def match_intent(self, user_query: str) -> Optional[Dict[str, Any]]:
        """Simple pattern-based intent matching using questions in templates."""
        if not user_query or not self._intent_templates:
            return None
        uq = user_query.strip().lower()
        # Try direct substring match against questions with placeholders removed
        for t in self._intent_templates:
            for q in t.get('questions', []):
                qn = q.lower()
                # Replace placeholders with a permissive pattern-like check
                qn = qn.replace('${project}', '').replace('${assignee}', '').replace('${issuetype}', '')
                qn = qn.replace('${status}', '').replace('${sprint}', '').replace('${version}', '')
                qn = qn.replace('${label}', '').replace('${component}', '')
                if qn and qn in uq:
                    return t
        # Fallback: rough keyword mapping by intent names
        for t in self._intent_templates:
            if t.get('intent') and t['intent'].replace('_', ' ') in uq:
                return t
        return None

    def build_jql(self, intent: Dict[str, Any], entities: Dict[str, str]) -> str:
        """Build JQL by replacing placeholders from entities with minimal cleanup."""
        jql = intent.get('jql', '')
        replacements = {
            'PROJECT': entities.get('PROJECT', entities.get('project', '*')),
            'ASSIGNEE': entities.get('ASSIGNEE', entities.get('assignee', '*')),
            'ISSUETYPE': entities.get('ISSUETYPE', entities.get('issuetype', '*')),
            'STATUS': entities.get('STATUS', entities.get('status', '*')),
            'SPRINT': entities.get('SPRINT', entities.get('sprint', '*')),
            'VERSION': entities.get('VERSION', entities.get('version', '*')),
            'LABEL': entities.get('LABEL', entities.get('label', '*')),
            'COMPONENT': entities.get('COMPONENT', entities.get('component', '*')),
            'PRIORITY': entities.get('PRIORITY', entities.get('priority', '*')),
            'DATE_RANGE': entities.get('DATE_RANGE', entities.get('date_range', '*')),
        }
        for key, val in replacements.items():
            jql = jql.replace(f"${{{key}}}", str(val))
        # Quote certain field values to avoid JQL keyword collisions (e.g., project = IS)
        def _quote_if_needed(v: str) -> str:
            if v is None:
                return v
            s = str(v).strip()
            if not s or s == '*':
                return s
            if (s.startswith('"') and s.endswith('"')) or '(' in s or ')' in s:
                return s
            return f'"{s}"'

        # Patterns to quote for '=' operator
        eq_fields = [
            'project', 'issuetype', 'status', 'priority', 'component', 'fixVersion', 'labels', 'label'
        ]

        for field in eq_fields:
            # Quote values in simple equality comparisons if not already quoted
            pattern = re.compile(rf"\b{field}\s*=\s*([^\s\)]+)")
            def repl(m):
                val = m.group(1)
                # Skip if already quoted
                if val.startswith('"') and val.endswith('"'):
                    return m.group(0)
                return f"{field} = {_quote_if_needed(val)}"
            jql = pattern.sub(repl, jql)

        # Normalize whitespace
        jql = ' '.join(jql.split())
        return jql

    async def run_query(self, jql: str, response_type: str = 'list') -> Dict[str, Any]:
        """Execute JQL and return Jira response in normalized shape."""
        max_results = 10 if response_type == 'list' else 0
        fields = ["id", "key", "summary", "status", "issuetype", "assignee", "project", "created", "updated"] if response_type == 'list' else None
        result = await self.search(jql, max_results=max_results or 0, fields=fields)
        return result

    async def _cache_fields(self):
        """Cache all JIRA fields for dynamic field resolution"""
        try:
            url = self._url("/rest/api/3/field")
            response = await self._client.get(url)
            response.raise_for_status()
            
            fields = response.json()
            self._field_cache = {}
            
            for field in fields:
                field_id = field.get('id')
                field_name = field.get('name')
                field_type = field.get('schema', {}).get('type', 'unknown')
                
                self._field_cache[field_id] = {
                    'name': field_name,
                    'type': field_type,
                    'custom': field.get('custom', False),
                    'searchable': field.get('searchable', False)
                }
                
                # Special handling for common fields
                if field_name == 'Sprint' and field.get('custom'):
                    self._sprint_field_id = field_id
                    logger.info(f"Discovered Sprint field ID: {field_id}")
            
            if not self._sprint_field_id:
                self._sprint_field_id = "customfield_10020"
                logger.warning("Using fallback Sprint field ID: customfield_10020")
                
        except Exception as e:
            logger.error(f"Failed to cache fields: {e}")
            await self._discover_sprint_field_fallback()

    async def _cache_assignees(self):
        """Cache assignee information for faster entity mapping"""
        try:
            # Get users from projects
            projects = await self.get_projects()
            self._assignee_cache = {}
            
            for project in projects:
                project_key = project.get('key')
                try:
                    # Correct Jira Cloud endpoint to fetch assignable users for a project
                    url = self._url("/rest/api/3/user/assignable/search")
                    params = {"project": project_key, "maxResults": 1000}
                    response = await self._client.get(url, params=params, headers=self._headers())
                    response.raise_for_status()
                    
                    users = response.json()
                    for user in users:
                        display_name = user.get('displayName', '')
                        account_id = user.get('accountId', '')
                        email = user.get('emailAddress', '')
                        
                        # Map by display name (case insensitive)
                        if display_name:
                            self._assignee_cache[display_name.lower()] = {
                                'accountId': account_id,
                                'displayName': display_name,
                                'email': email
                            }
                            
                except Exception as e:
                    logger.warning(f"Failed to get assignees for project {project_key}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to cache assignees: {e}")

    async def _cache_projects(self):
        """Cache project information"""
        try:
            url = self._url("/rest/api/3/project")
            response = await self._client.get(url)
            response.raise_for_status()
            
            projects = response.json()
            self._project_cache = {}
            
            for project in projects:
                project_key = project.get('key')
                self._project_cache[project_key] = {
                    'key': project_key,
                    'name': project.get('name', ''),
                    'description': project.get('description', ''),
                    'projectTypeKey': project.get('projectTypeKey', ''),
                    'lead': project.get('lead', {}).get('displayName', '')
                }
                
        except Exception as e:
            logger.error(f"Failed to cache projects: {e}")

    async def _discover_sprint_field_fallback(self):
        """Fallback method for sprint field discovery"""
        try:
            url = self._url("/rest/api/3/field")
            response = await self._client.get(url)
            response.raise_for_status()
            
            fields = response.json()
            for field in fields:
                if field.get('name') == 'Sprint' and field.get('custom'):
                    self._sprint_field_id = field['id']
                    logger.info(f"Discovered Sprint field ID: {self._sprint_field_id}")
                    break
            
            if not self._sprint_field_id:
                self._sprint_field_id = "customfield_10020"
                logger.warning("Using fallback Sprint field ID: customfield_10020")
                
        except Exception as e:
            logger.error(f"Failed to discover Sprint field: {e}")
            self._sprint_field_id = "customfield_10020"

    def _url(self, path: str) -> str:
        # Ensure base_url doesn't end with slash and path starts with slash
        base_url = self.cfg.base_url.rstrip("/")
        if not path.startswith("/"):
            path = "/" + path
        return f"{base_url}{path}"

    def get_field_id(self, field_name: str) -> Optional[str]:
        """Get field ID by name from cache"""
        if not self._field_cache:
            return None
        
        for field_id, field_info in self._field_cache.items():
            if field_info['name'].lower() == field_name.lower():
                return field_id
        return None

    def get_assignee_info(self, name: str) -> Optional[Dict[str, str]]:
        """Get assignee info by name from cache"""
        if not self._assignee_cache:
            return None
        return self._assignee_cache.get(name.lower())

    def get_project_info(self, project_key: str) -> Optional[Dict[str, Any]]:
        """Get project info by key from cache"""
        if not self._project_cache:
            return None
        return self._project_cache.get(project_key.upper())

    def get_known_project_keys(self) -> List[str]:
        """Return known project keys from cache (best-effort, non-async)."""
        if not self._project_cache:
            return []
        return list(self._project_cache.keys())

    def get_known_assignee_names(self) -> List[str]:
        """Return known assignee display names from cache (best-effort)."""
        if not self._assignee_cache:
            return []
        # Stored as lowercased keys; return display names from values
        names: List[str] = []
        for info in self._assignee_cache.values():
            dn = info.get('displayName')
            if dn:
                names.append(dn)
        return names

    def is_cache_valid(self, max_age_minutes: int = 30) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False
        return datetime.now() - self._cache_timestamp < timedelta(minutes=max_age_minutes)

    async def refresh_cache_if_needed(self):
        """Refresh cache if it's expired"""
        if not self.is_cache_valid():
            logger.info("Cache expired, refreshing...")
            await self._initialize_caches()

    async def _get_with_retry(self, url: str, max_retries: int = 3) -> httpx.Response:
        """Make GET request with retry logic and rate limiting"""
        for attempt in range(max_retries):
            try:
                response = await self._client.get(url)
                
                if response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [400, 410]:
                    # HTTP 400/410 - don't retry, log response body
                    logger.error(f"[Jira] Request failed ({e.response.status_code}): {url}")
                    try:
                        error_body = e.response.text
                        logger.error(f"[Jira] Response body: {error_body}")
                    except Exception:
                        logger.error(f"[Jira] Could not read response body")
                    raise
                elif e.response.status_code >= 500 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Server error {e.response.status_code}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise
        
        raise Exception(f"Failed after {max_retries} attempts")

    async def _search_with_pagination(self, jql: str, max_results: int = 1000) -> Dict[str, Any]:
        """Search with pagination support (POST /rest/api/3/search to avoid 410/414 on long URLs)."""
        all_issues: List[Dict[str, Any]] = []
        start_at = 0
        max_results_per_page = min(100, max_results)  # Jira max is 100 per page
        
        # Local helper to POST with basic retry using existing client
        async def _post_search(start: int, size: int) -> Dict[str, Any]:
            url = self._url("/rest/api/3/search")
            payload = {"jql": jql, "startAt": start, "maxResults": size}
            # Prefer json body per Jira Cloud API
            for attempt in range(3):
                try:
                    if not self._client:
                        await self.initialize()
                    resp = await self._client.post(url, json=payload, headers={"Content-Type": "application/json"})
                    resp.raise_for_status()
                    return resp.json()
                except Exception as e:
                    if attempt == 2:
                        raise
                    wait = 2 ** attempt
                    logger.warning(f"Search POST failed (attempt {attempt+1}): {e}; retrying in {wait}s")
                    await asyncio.sleep(wait)
            return {"issues": [], "total": 0}

        data: Dict[str, Any] = {"issues": [], "total": 0}
        while len(all_issues) < max_results:
            remaining = max_results - len(all_issues)
            current_max = min(max_results_per_page, remaining)
            
            data = await _post_search(start_at, current_max)
            issues = data.get("issues", [])
            if not issues:
                break
                
            all_issues.extend(issues)
            start_at += len(issues)
            if len(issues) < current_max:
                break
        
        return {"issues": all_issues[:max_results], "total": data.get("total", len(all_issues))}

    # Agile: current sprint for the configured board
    async def get_current_sprint(self) -> Optional[Dict[str, Any]]:
        if not self.cfg.board_id:
            return None
        
        try:
            # Try Agile API first (updated for Jira Cloud)
            url = self._url(f"/rest/agile/1.0/board/{self.cfg.board_id}/sprint?state=active")
            response = await self._get_with_retry(url)
            data = response.json()
            
            sprints = data.get('values', [])
            if sprints:
                return sprints[0]  # Return first active sprint
            
            # Fallback to closed sprints if no active ones
            url = self._url(f"/rest/agile/1.0/board/{self.cfg.board_id}/sprint?state=closed")
            response = await self._get_with_retry(url)
            data = response.json()
            
            sprints = data.get('values', [])
            if sprints:
                return sprints[-1]  # Return most recent closed sprint
                
        except Exception as e:
            logger.error(f"Error getting current sprint: {e}")
        
        return None

    def _headers(self):
        """Standard headers for Jira API requests"""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_issue(self, key: str, fields=None, expand=None):
        """Get a specific issue by key"""
        url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/issue/{key}"
        params = {}
        if fields: 
            params["fields"] = ",".join(fields)
        if expand: 
            params["expand"] = ",".join(expand)
        
        resp = await self._client.get(url, params=params, headers=self._headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def count(self, jql: str) -> int:
        """Fast count using approximate-count endpoint with v2 fallback"""
        # Try API v3 approximate-count first
        try:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/search/approximate-count"
            resp = await self._client.post(url, json={"jql": jql}, headers=self._headers())
            if resp.status_code == 200:
                return int(resp.json().get("count", 0))
            elif resp.status_code == 404:
                logger.warning("API v3 approximate-count not available, trying v2 search")
            else:
                logger.warning(f"API v3 approximate-count returned {resp.status_code}, trying v2 search")
        except Exception as e:
            logger.warning(f"API v3 approximate-count failed: {e}, trying v2 search")
        
        # Fallback to API v2 search with maxResults=0
        try:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/2/search"
            params = {"jql": jql, "maxResults": 0}
            resp = await self._client.get(url, params=params, headers=self._headers())
            if resp.status_code == 200:
                data = resp.json()
                count = int(data.get("total", 0))
                logger.info(f"Successfully used API v2 count: {count}")
                return count
            else:
                logger.error(f"API v2 count returned {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"API v2 count failed: {e}")
        
        # Final fallback
        logger.warning(f"[Jira] All count endpoints failed for JQL: {jql}")
        return 0

    async def get_project_keys(self) -> List[str]:
        """Get all project keys from Jira with v2 fallback"""
        # Try API v3 first
        try:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/project/search"
            resp = await self._client.get(url, headers=self._headers())
            if resp.status_code == 200:
                data = resp.json()
                keys = [p.get("key") for p in (data.get("values") or []) if p.get("key")]
                logger.info(f"Successfully used API v3 project search: {len(keys)} projects found")
                return keys
            else:
                logger.warning(f"API v3 project search returned {resp.status_code}, trying v2")
        except Exception as e:
            logger.warning(f"API v3 project search failed: {e}, trying v2")
        
        # Fallback to API v2
        try:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/2/project"
            resp = await self._client.get(url, headers=self._headers())
            if resp.status_code == 200:
                data = resp.json()
                keys = [p.get("key") for p in data if p.get("key")]
                logger.info(f"Successfully used API v2 project search: {len(keys)} projects found")
                return keys
            else:
                logger.error(f"API v2 project search returned {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"API v2 project search failed: {e}")
        
        # Final fallback
        logger.warning("[Jira] All project search endpoints failed")
        return []

    async def search(self, jql: str, max_results: int = 50, fields=None, start_at: int = 0, expand=None):
        """
        Search issues using the correct Jira REST API v3 endpoints
        """
        if not self._client:
            await self.initialize()

        # Try the correct API v3 endpoint first: GET /rest/api/3/search/jql with query params
        try:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/search/jql"
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results
            }
            if fields:
                params["fields"] = ",".join(fields) if isinstance(fields, list) else fields
            resp = await self._client.get(url, params=params, headers=self._headers())

            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Successfully used API v3 GET search/jql: {len(data.get('issues', []))} issues found")
                return data
            elif resp.status_code == 410:
                logger.warning("API v3 search/jql returned 410 Gone, trying legacy search")
            else:
                try:
                    logger.error(f"[Jira] v3 search/jql {resp.status_code}: {resp.text}")
                except Exception:
                    pass
                logger.warning(f"API v3 search/jql returned {resp.status_code}, trying legacy search")
                
        except Exception as e:
            logger.warning(f"API v3 search/jql failed: {e}, trying legacy search")

        # Fallback to legacy API v3 search
        try:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/search"
            payload = {
                "jql": jql,
                "maxResults": max_results,
                "startAt": start_at,
                "fields": fields or ["id", "key", "summary", "status", "issuetype", "assignee", "project", "created", "updated"]
            }
            resp = await self._client.post(url, json=payload, headers=self._headers())
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Successfully used legacy API v3 search: {len(data.get('issues', []))} issues found")
                return data
            elif resp.status_code == 410:
                logger.warning("Legacy API v3 search returned 410 Gone, trying API v2")
            else:
                try:
                    logger.error(f"[Jira] legacy v3 search {resp.status_code}: {resp.text}")
                except Exception:
                    pass
                logger.warning(f"Legacy API v3 search returned {resp.status_code}, trying API v2")
                
        except Exception as e:
            logger.warning(f"Legacy API v3 search failed: {e}, trying API v2")

        # Final fallback to API v2
        try:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/2/search"
            params = {
                "jql": jql,
                "maxResults": max_results,
                "startAt": start_at
            }
            if fields:
                params["fields"] = ",".join(fields) if isinstance(fields, list) else fields
            
            resp = await self._client.get(url, params=params, headers=self._headers())
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Successfully used API v2 search: {len(data.get('issues', []))} issues found")
                return data
            else:
                try:
                    logger.error(f"API v2 search returned {resp.status_code}: {resp.text}")
                except Exception:
                    pass
                
        except Exception as e:
            logger.error(f"API v2 search failed: {e}")
        
        # Final fallback - return empty result
        logger.warning(f"[Jira] All search endpoints failed. Returning empty result for JQL: {jql}")
        return {"issues": [], "total": 0}
    
    async def _get_recent_project_issues(self, project_key: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get recent issues from a specific project as workaround for search API"""
        try:
            # Try multiple approaches to get issues
            approaches = [
                # Approach 1: Project issues endpoint
                f"{self.cfg.base_url.rstrip('/')}/rest/api/3/project/{project_key}/issues",
                # Approach 2: Search with project filter (might work even if general search doesn't)
                f"{self.cfg.base_url.rstrip('/')}/rest/api/3/search",
            ]
            
            for url in approaches:
                try:
                    if "project" in url and "issues" in url:
                        # Project issues endpoint
                        params = {
                            "maxResults": max_results,
                            "fields": "id,key,summary,status,issuetype,assignee,project,created,updated"
                        }
                        resp = await self._client.get(url, params=params, headers=self._headers())
                    else:
                        # Search endpoint with project filter
                        payload = {
                            "jql": f"project = {project_key} ORDER BY updated DESC",
                            "maxResults": max_results,
                            "fields": ["id", "key", "summary", "status", "issuetype", "assignee", "project", "created", "updated"]
                        }
                        resp = await self._client.post(url, json=payload, headers=self._headers())
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        issues = data.get('issues', [])
                        if issues:
                            logger.info(f"Successfully got {len(issues)} issues from {url}")
                            return issues
                    else:
                        logger.debug(f"Approach {url} returned {resp.status_code}")
                        
                except Exception as e:
                    logger.debug(f"Approach {url} failed: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"All approaches failed for project {project_key}: {e}")
        
        return []
    
    async def _get_issues_from_all_projects(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get recent issues from all projects as workaround for search API"""
        try:
            # Get all project keys
            project_keys = await self.get_project_keys()
            logger.debug(f"Found {len(project_keys)} projects: {project_keys}")
            
            all_issues = []
            for project_key in project_keys[:5]:  # Limit to first 5 projects to avoid too many API calls
                try:
                    project_issues = await self._get_recent_project_issues(project_key, max_results // len(project_keys))
                    all_issues.extend(project_issues)
                    logger.debug(f"Got {len(project_issues)} issues from project {project_key}")
                except Exception as e:
                    logger.debug(f"Failed to get issues from project {project_key}: {e}")
                    continue
            
            # Sort by updated date (most recent first)
            try:
                all_issues.sort(key=lambda x: x.get('fields', {}).get('updated', ''), reverse=True)
            except Exception:
                pass
                
            logger.info(f"Retrieved {len(all_issues)} total issues from all projects")
            return all_issues[:max_results]
            
        except Exception as e:
            logger.warning(f"Failed to get issues from all projects: {e}")
            return []

    async def count(self, jql: str) -> int:
        """
        Fast approximate count based on Enhanced JQL.
        """
        url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/search/approximate-count"
        
        if not self._client:
            await self.initialize()
            
        resp = await self._client.post(url, json={"jql": jql}, headers=self._headers())
        if resp.status_code == 410:
            # Some sites may not have approximate-count enabled; caller should fall back to search().total
            logger.warning("[Jira] Approximate count API unavailable. Fallback required.")
            raise RuntimeError("Approximate count API unavailable. Fallback required.")
        resp.raise_for_status()
        data = resp.json()
        return int(data.get("count", 0))

    async def get_issue(self, key: str, fields=None, expand=None) -> Dict[str, Any]:
        """
        Get a specific issue by key using /rest/api/3/issue/{key}
        """
        if not self._client:
            await self.initialize()
        
        url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/issue/{key}"
        params = {}
        
        if fields:
            params["fields"] = ",".join(fields) if isinstance(fields, list) else fields
        if expand:
            params["expand"] = ",".join(expand) if isinstance(expand, list) else expand
        
        try:
            resp = await self._client.get(url, params=params, headers=self._headers())
            
            # Log non-2xx responses with body
            if not (200 <= resp.status_code < 300):
                logger.error(f"[Jira] Issue lookup failed for {key}: {resp.status_code}")
                try:
                    error_body = resp.text
                    logger.error(f"[Jira] Response body: {error_body}")
                except Exception:
                    logger.error(f"[Jira] Could not read response body")
                resp.raise_for_status()
            
            return resp.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [400, 410]:
                # Don't retry on 400/410
                logger.error(f"[Jira] Issue lookup failed for {key}: {e.response.status_code}")
                try:
                    error_body = e.response.text
                    logger.error(f"[Jira] Response body: {error_body}")
                except Exception:
                    logger.error(f"[Jira] Could not read response body")
                raise
            else:
                # Retry for other errors
                raise
        except Exception as e:
            logger.error(f"[Jira] Issue lookup error for {key}: {e}")
            raise

    async def get_board_info(self) -> Optional[Dict[str, Any]]:
        """Get board information"""
        if not self.cfg.board_id:
            return None
        
        try:
            url = self._url(f"/rest/agile/1.0/board/{self.cfg.board_id}")
            response = await self._get_with_retry(url)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting board info: {e}")
            return None

    async def get_backlog_items(self, sprint_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get backlog items - either from a specific sprint or general backlog"""
        if not self.cfg.board_id:
            return []
        
        try:
            if sprint_id:
                # Get items from specific sprint
                url = self._url(f"/rest/agile/1.0/sprint/{sprint_id}/issue")
            else:
                # Get backlog items
                url = self._url(f"/rest/agile/1.0/board/{self.cfg.board_id}/backlog")
            
            response = await self._get_with_retry(url)
            result = response.json()
            return result.get('issues', [])
        except Exception as e:
            logger.error(f"Error getting backlog items: {e}")
            return []

    async def get_sprint_items(self, sprint_id: str) -> List[Dict[str, Any]]:
        """Get all items from a specific sprint"""
        try:
            url = self._url(f"/rest/agile/1.0/sprint/{sprint_id}/issue")
            response = await self._get_with_retry(url)
            if response:
                result = response.json()
                return result.get('issues', [])
            return []
        except Exception as e:
            logger.error(f"Error getting sprint items: {e}")
            return []

    async def get_all_sprints(self) -> List[Dict[str, Any]]:
        """Get all sprints for the board"""
        if not self.cfg.board_id:
            return []
        
        try:
            url = self._url(f"/rest/agile/1.0/board/{self.cfg.board_id}/sprint")
            response = await self._get_with_retry(url)
            result = response.json()
            return result.get('values', [])
        except Exception as e:
            logger.error(f"Error getting all sprints: {e}")
            return []

    async def get_project_info(self, project_key: str) -> Optional[Dict[str, Any]]:
        """Get project information"""
        try:
            url = self._url(f"/rest/api/3/project/{project_key}")
            response = await self._get_with_retry(url)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting project info: {e}")
            return None

    async def get_issue_details(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific issue"""
        try:
            url = self._url(f"/rest/api/3/issue/{issue_key}")
            response = await self._get_with_retry(url)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting issue details: {e}")
            return None

    async def get_issue_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get comments for a specific issue"""
        try:
            url = self._url(f"/rest/api/3/issue/{issue_key}/comment")
            response = await self._get_with_retry(url)
            result = response.json()
            return result.get('comments', [])
        except Exception as e:
            logger.error(f"Error getting issue comments: {e}")
            return []

    async def get_issue_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get available transitions for an issue"""
        try:
            url = self._url(f"/rest/api/3/issue/{issue_key}/transitions")
            response = await self._get_with_retry(url)
            result = response.json()
            return result.get('transitions', [])
        except Exception as e:
            logger.error(f"Error getting issue transitions: {e}")
            return []

    async def resolve_assignee_to_account_id(self, assignee_name: str) -> Optional[str]:
        """Resolve assignee name to account ID for Jira Cloud"""
        try:
            url = self._url(f"/rest/api/3/user/search?query={assignee_name}")
            response = await self._get_with_retry(url)
            users = response.json()
            
            name_lower = (assignee_name or '').lower()
            # 1) Exact display/email match
            for user in users:
                if (user.get('displayName', '').lower() == name_lower or 
                    user.get('emailAddress', '').lower() == name_lower):
                    return user.get('accountId')
            # 2) Contains/alias match (partial name)
            candidates = [u for u in users if name_lower in (u.get('displayName', '') or '').lower()]
            if len(candidates) == 1:
                return candidates[0].get('accountId')
            
            return None
        except Exception as e:
            logger.error(f"Error resolving assignee {assignee_name}: {e}")
            return None

    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects using the optimized project search endpoint"""
        try:
            url = self._url("/rest/api/3/project/search")
            response = await self._get_with_retry(url)
            result = response.json()
            return result.get('values', [])
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []

    async def build_assignee_jql(self, assignee_name: str) -> str:
        """Build JQL with proper account ID for assignee queries"""
        account_id = await self.resolve_assignee_to_account_id(assignee_name)
        if account_id:
            return f"assignee in ({account_id})"
        else:
            # Fallback to name-based fuzzy search
            return f'assignee ~ "{assignee_name}"'
    
    async def get_assignees_for_project(self, project_key: str) -> set:
        """Get all assignees for a specific project"""
        try:
            # Try to get assignees from project endpoint
            url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/project/{project_key}/assignable"
            resp = await self._client.get(url, headers=self._headers())
            
            if resp.status_code == 200:
                data = resp.json()
                assignees = set()
                for user in data:
                    if user.get('displayName'):
                        assignees.add(user.get('displayName'))
                return assignees
            else:
                logger.warning(f"Could not get assignees for project {project_key}: {resp.status_code}")
                return set()
                
        except Exception as e:
            logger.warning(f"Error getting assignees for project {project_key}: {e}")
            return set()

    async def _get(self, path: str, params=None):
        """Internal GET method for making API requests"""
        if not self._client:
            await self.initialize()
        
        url = self._url(path)
        if params:
            # Convert params to query string
            query_params = []
            for key, value in params.items():
                query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        
        response = await self._get_with_retry(url)
        return response.json()

    async def get_fields(self):
        """Get all Jira fields"""
        if not self._client:
            await self.initialize()
        url = f"{self.cfg.base_url.rstrip('/')}/rest/api/3/field"
        response = await self._client.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    async def get_sprints_all(self, board_id: int, states: str = "active,future,closed", page_size: int = 50):
        """
        Fetch all sprints for a board across pages (Agile API).
        """
        sprints, start_at = [], 0
        
        if not self._client:
            await self.initialize()
        
        while True:
            url = f"{self.cfg.base_url.rstrip('/')}/rest/agile/1.0/board/{board_id}/sprint"
            params = {"state": states, "startAt": start_at, "maxResults": page_size}
            resp = await self._client.get(url, params=params, headers=self._headers())
            resp.raise_for_status()
            page = resp.json()
            values = page.get("values") or page.get("sprints") or []
            sprints.extend(values)
            if page.get("isLast") or len(values) < page_size:
                break
            start_at += page_size
        return sprints

    async def get_latest_closed_sprint_id(self, board_id: int) -> Optional[int]:
        """
        Get the latest closed sprint ID for fallback when no active sprint exists.
        """
        try:
            sprints = await self.get_sprints_all(board_id, states="closed", page_size=50)
            if not sprints:
                return None
            
            # Sort by end date (most recent first)
            closed_sprints = [s for s in sprints if s.get('state') == 'closed']
            if not closed_sprints:
                return None
                
            # Sort by end date descending
            closed_sprints.sort(key=lambda x: x.get('endDate', ''), reverse=True)
            latest_sprint = closed_sprints[0]
            return latest_sprint.get('id')
            
        except Exception as e:
            logger.error(f"Failed to get latest closed sprint: {e}")
            return None