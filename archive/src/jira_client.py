from __future__ import annotations
import httpx
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import quote
from datetime import datetime, timedelta
from auth import JiraConfig
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

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            auth=(self.cfg.email, self.cfg.api_token),
            timeout=httpx.Timeout(60.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        await self._initialize_caches()
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
            projects = await self._get_projects()
            self._assignee_cache = {}
            
            for project in projects:
                project_key = project.get('key')
                try:
                    url = self._url(f"/rest/api/3/project/{project_key}/assignable")
                    response = await self._client.get(url)
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
                if e.response.status_code >= 500 and attempt < max_retries - 1:
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
        """Search with pagination support"""
        all_issues = []
        start_at = 0
        max_results_per_page = min(100, max_results)  # Jira max is 100 per page
        
        while len(all_issues) < max_results:
            remaining = max_results - len(all_issues)
            current_max = min(max_results_per_page, remaining)
            
            # URL-encode JQL to avoid spaces/special char issues (no spaces in safe set)
            jql_encoded = quote(jql, safe=":=(),\"'+-_./")
            url = self._url(f"/rest/api/3/search?jql={jql_encoded}&startAt={start_at}&maxResults={current_max}")
            response = await self._get_with_retry(url)
            data = response.json()
            
            issues = data.get('issues', [])
            if not issues:
                break
                
            all_issues.extend(issues)
            start_at += len(issues)
            
            # Check if we've reached the end
            if len(issues) < current_max:
                break
        
        return {
            'issues': all_issues[:max_results],
            'total': data.get('total', len(all_issues))
        }

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

    async def search(self, jql: str, max_results: int = 100) -> Dict[str, Any]:
        """Search issues with JQL"""
        try:
            return await self._search_with_pagination(jql, max_results)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {'issues': [], 'total': 0}

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
            
            for user in users:
                if (user.get('displayName', '').lower() == assignee_name.lower() or 
                    user.get('emailAddress', '').lower() == assignee_name.lower()):
                    return user.get('accountId')
            
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
            # Fallback to name-based search
            return f'assignee = "{assignee_name}"'

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
        return await self._get("/rest/api/3/field")

    async def get_sprints_all(self, board_id: int, states: str = "active,future,closed", page_size: int = 50):
        """Get all sprints for a board with pagination support"""
        sprints = []
        start_at = 0
        
        while True:
            page = await self._get(f"/rest/agile/1.0/board/{board_id}/sprint",
                                   params={"state": states, "startAt": start_at, "maxResults": page_size})
            values = page.get("values") or page.get("sprints") or []
            sprints.extend(values)
            
            if page.get("isLast") or len(values) < page_size:
                break
            start_at += page_size
        
        return sprints