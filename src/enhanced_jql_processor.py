"""
Enhanced JQL Processing Layer
Implements advanced JQL features including multi-entity handling, fallback queries, 
pre-aggregation, risk identification, URL enrichment, and response validation.
"""

import re
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ResponseFormat(Enum):
    TEXT = "text"
    JSON = "json"

@dataclass
class JQLQuery:
    """Represents a JQL query with metadata"""
    query: str
    description: str
    priority: int = 1
    fallback_queries: List[str] = None
    
    def __post_init__(self):
        if self.fallback_queries is None:
            self.fallback_queries = []

@dataclass
class QueryResult:
    """Represents the result of a JQL query execution"""
    issues: List[Dict[str, Any]]
    total_count: int
    jql_used: str
    execution_time_ms: int
    has_more: bool = False
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

@dataclass
class AggregatedData:
    """Pre-aggregated counts and metrics"""
    total_issues: int
    done_count: int
    in_progress_count: int
    to_do_count: int
    blocked_count: int
    by_assignee: Dict[str, int]
    by_project: Dict[str, int]
    by_issue_type: Dict[str, int]
    risks: List[Dict[str, Any]]
    oldest_tickets: List[Dict[str, Any]]
    recently_updated: List[Dict[str, Any]]

class EnhancedJQLProcessor:
    """Enhanced JQL processor with advanced features"""
    
    def __init__(self, jira_client):
        self.jira_client = jira_client
        self.conversation_memory = []  # Store last 10 interactions
        self.current_sprint_cache = None
        self.cache_timestamp = None
        
    async def process_query(self, query: str, format: ResponseFormat = ResponseFormat.TEXT) -> Dict[str, Any]:
        """Process a user query with enhanced JQL features"""
        
        # Store in conversation memory
        self._add_to_memory(query)
        
        # Analyze query for multi-entity handling
        entities = self._extract_entities(query)
        
        # Generate JQL queries (potentially multiple for comparisons)
        jql_queries = await self._generate_jql_queries(query, entities)
        
        # Execute queries with fallback support
        results = await self._execute_queries_with_fallback(jql_queries)
        
        # Pre-aggregate data
        aggregated_data = self._aggregate_data(results)
        
        # Identify risks
        risks = self._identify_risks(results)
        
        # Enrich with URLs
        enriched_results = self._enrich_with_urls(results)
        
        # Generate response
        if format == ResponseFormat.JSON:
            response = self._generate_json_response(enriched_results, aggregated_data, risks)
        else:
            response = self._generate_text_response(enriched_results, aggregated_data, risks, query)
        
        # Validate response
        validated_response = self._validate_response(response, query)
        
        return {
            'response': validated_response,
            'format': format.value,
            'data': enriched_results,
            'aggregated': aggregated_data,
            'risks': risks,
            'conversation_context': self._get_recent_context()
        }
    
    def _add_to_memory(self, query: str):
        """Add query to conversation memory"""
        self.conversation_memory.append({
            'query': query,
            'timestamp': datetime.now(),
            'entities': self._extract_entities(query)
        })
        
        # Keep only last 10 interactions
        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query with improved pattern matching"""
        entities = {
            'assignees': [],
            'projects': [],
            'issue_types': [],
            'statuses': [],
            'keywords': [],
            'tickets': []
        }
        
        query_lower = query.lower()
        
        # Extract ticket references (PROJ-123, CCM-456, etc.)
        ticket_pattern = r'\b([A-Z]{2,}-\d+)\b'
        entities['tickets'] = re.findall(ticket_pattern, query)
        
        # Extract assignee names (common patterns)
        assignee_patterns = [
            r'\b(ajith|kumar|ashwin|thyagarajan|priya|john|jane|mike|sarah|david|lisa)\b',
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'  # Full names
        ]
        for pattern in assignee_patterns:
            matches = re.findall(pattern, query_lower)
            entities['assignees'].extend([m.title() if isinstance(m, str) else ' '.join(m).title() for m in matches])
        
        # Extract project keys
        project_pattern = r'\b(CCM|CES|GTMS|TI|PROJ)\b'
        entities['projects'] = re.findall(project_pattern, query.upper())
        
        # Extract issue types
        issue_type_patterns = ['story', 'bug', 'task', 'epic', 'subtask']
        for itype in issue_type_patterns:
            if itype in query_lower:
                entities['issue_types'].append(itype.title())
        
        # Extract statuses
        status_patterns = ['done', 'in progress', 'to do', 'blocked', 'closed', 'open']
        for status in status_patterns:
            if status in query_lower:
                entities['statuses'].append(status.title())
        
        # Extract keywords for context
        keywords = ['sprint', 'current', 'this week', 'last week', 'today', 'yesterday', 'compare', 'vs', 'versus']
        for keyword in keywords:
            if keyword in query_lower:
                entities['keywords'].append(keyword)
        
        return entities
    
    async def _generate_jql_queries(self, query: str, entities: Dict[str, List[str]]) -> List[JQLQuery]:
        """Generate JQL queries with multi-entity support"""
        queries = []
        
        # Check for comparison queries
        if any(comp_word in query.lower() for comp_word in ['compare', 'vs', 'versus', 'against']):
            queries.extend(await self._generate_comparison_queries(query, entities))
        else:
            queries.extend(await self._generate_single_queries(query, entities))
        
        return queries
    
    async def _generate_comparison_queries(self, query: str, entities: Dict[str, List[str]]) -> List[JQLQuery]:
        """Generate multiple JQL queries for comparison scenarios"""
        queries = []
        
        # Extract multiple assignees for comparison
        assignees = entities.get('assignees', [])
        if len(assignees) >= 2:
            for assignee in assignees:
                assignee_info = self.jira_client.get_assignee_info(assignee)
                if assignee_info:
                    jql = f'assignee = "{assignee_info["accountId"]}"'
                    queries.append(JQLQuery(
                        query=jql,
                        description=f"Tickets assigned to {assignee}",
                        priority=1
                    ))
        
        # Extract multiple projects for comparison
        projects = entities.get('projects', [])
        if len(projects) >= 2:
            for project in projects:
                jql = f'project = "{project}"'
                queries.append(JQLQuery(
                    query=jql,
                    description=f"Tickets in project {project}",
                    priority=1
                ))
        
        return queries
    
    async def _generate_single_queries(self, query: str, entities: Dict[str, List[str]]) -> List[JQLQuery]:
        """Generate single JQL query based on entities"""
        jql_parts = []
        
        # Sprint context - use same logic as Jira UI with fallback
        if 'sprint' in query.lower() or 'current' in query.lower():
            # First try openSprints() function like Jira UI
            jql_parts.append('sprint in openSprints()')
            
            # Add fallback for when no active sprint exists
            try:
                # Check if we have a board_id to get latest closed sprint
                if hasattr(self.jira_client, 'cfg') and self.jira_client.cfg.board_id:
                    latest_closed_sprint_id = await self.jira_client.get_latest_closed_sprint_id(self.jira_client.cfg.board_id)
                    if latest_closed_sprint_id:
                        # Add fallback query using latest closed sprint
                        fallback_sprint_query = f'sprint = {latest_closed_sprint_id}'
                        logger.info(f"Added fallback sprint query: {fallback_sprint_query}")
            except Exception as e:
                logger.warning(f"Could not get latest closed sprint for fallback: {e}")
        
        # Assignee filter
        assignees = entities.get('assignees', [])
        if assignees:
            assignee_conditions = []
            for assignee in assignees:
                assignee_info = self.jira_client.get_assignee_info(assignee)
                if assignee_info:
                    assignee_conditions.append(f'assignee = "{assignee_info["accountId"]}"')
                else:
                    # Fallback to name matching
                    assignee_conditions.append(f'assignee ~ "{assignee}"')
            
            if assignee_conditions:
                jql_parts.append(f'({" OR ".join(assignee_conditions)})')
        
        # Project filter
        projects = entities.get('projects', [])
        if projects:
            project_conditions = [f'project = "{proj}"' for proj in projects]
            jql_parts.append(f'({" OR ".join(project_conditions)})')
        
        # Issue type filter
        issue_types = entities.get('issue_types', [])
        if issue_types:
            type_conditions = [f'issuetype = "{itype}"' for itype in issue_types]
            jql_parts.append(f'({" OR ".join(type_conditions)})')
        
        # Status filter
        statuses = entities.get('statuses', [])
        if statuses:
            status_conditions = [f'status = "{status}"' for status in statuses]
            jql_parts.append(f'({" OR ".join(status_conditions)})')
        
        # Time-based filters
        if 'this week' in query.lower():
            jql_parts.append('updated >= startOfWeek()')
        elif 'last week' in query.lower():
            jql_parts.append('updated >= startOfWeek(-1) AND updated < startOfWeek()')
        elif 'today' in query.lower():
            jql_parts.append('updated >= startOfDay()')
        elif 'yesterday' in query.lower():
            jql_parts.append('updated >= startOfDay(-1) AND updated < startOfDay()')
        
        # Build final JQL
        base_jql = ' AND '.join(jql_parts) if jql_parts else 'ORDER BY updated DESC'
        final_jql = f'{base_jql} ORDER BY updated DESC'
        
        # Log the generated JQL for debugging
        logger.info(f"Generated JQL for sprint query: {final_jql}")
        
        # Generate fallback queries
        fallback_queries = []
        if jql_parts:
            # For sprint queries, add specific sprint fallbacks
            if 'sprint' in query.lower() or 'current' in query.lower():
                try:
                    if hasattr(self.jira_client, 'cfg') and self.jira_client.cfg.board_id:
                        latest_closed_sprint_id = await self.jira_client.get_latest_closed_sprint_id(self.jira_client.cfg.board_id)
                        if latest_closed_sprint_id:
                            # Replace openSprints() with specific sprint ID
                            sprint_fallback_parts = [part.replace('sprint in openSprints()', f'sprint = {latest_closed_sprint_id}') for part in jql_parts]
                            sprint_fallback_jql = ' AND '.join(sprint_fallback_parts)
                            fallback_queries.append(f'{sprint_fallback_jql} ORDER BY updated DESC')
                            logger.info(f"Added sprint fallback: {sprint_fallback_jql}")
                except Exception as e:
                    logger.warning(f"Could not create sprint fallback: {e}")
            
            # Remove sprint filter entirely (but only if it's not a sprint-specific question)
            if not ('sprint' in query.lower() or 'current' in query.lower()):
                fallback_jql = ' AND '.join([part for part in jql_parts if 'sprint' not in part.lower()])
                if fallback_jql:
                    fallback_queries.append(f'{fallback_jql} ORDER BY updated DESC')
            else:
                # For sprint questions, ensure we don't degrade to project-level queries
                logger.info("Sprint-specific question detected - avoiding project-level fallback")
            
            # Expand time range
            time_fallback = ' AND '.join([part for part in jql_parts if 'updated' not in part.lower()])
            if time_fallback:
                fallback_queries.append(f'{time_fallback} AND updated >= -30d ORDER BY updated DESC')
        
        return [JQLQuery(
            query=final_jql,
            description="Primary query",
            priority=1,
            fallback_queries=fallback_queries
        )]
    
    async def _execute_queries_with_fallback(self, queries: List[JQLQuery]) -> List[QueryResult]:
        """Execute queries with fallback support"""
        results = []
        
        for jql_query in queries:
            result = await self._execute_single_query(jql_query)
            results.append(result)
        
        return results
    
    async def _execute_single_query(self, jql_query: JQLQuery) -> QueryResult:
        """Execute a single JQL query with fallback support"""
        start_time = datetime.now()
        
        try:
            # Try primary query
            issues = await self.jira_client.search(jql_query.query, max_results=100)
            
            if issues.get('total', 0) == 0 and jql_query.fallback_queries:
                # Try fallback queries
                for fallback_jql in jql_query.fallback_queries:
                    fallback_issues = await self.jira_client.search(fallback_jql, max_results=100)
                    if fallback_issues.get('total', 0) > 0:
                        issues = fallback_issues
                        jql_query.query = fallback_jql  # Update to show which query worked
                        break
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log result for debugging
            logger.info(f"JQL '{jql_query.query}' returned {issues.get('total', 0)} total issues")
            if issues.get('issues'):
                first_few_keys = [issue.get('key') for issue in issues.get('issues', [])[:3]]
                logger.info(f"First few ticket keys: {first_few_keys}")
            
            return QueryResult(
                issues=issues.get('issues', []),
                total_count=issues.get('total', 0),
                jql_used=jql_query.query,
                execution_time_ms=int(execution_time),
                has_more=issues.get('total', 0) > len(issues.get('issues', []))
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return QueryResult(
                issues=[],
                total_count=0,
                jql_used=jql_query.query,
                execution_time_ms=int(execution_time),
                errors=[str(e)]
            )
    
    def _aggregate_data(self, results: List[QueryResult]) -> AggregatedData:
        """Pre-aggregate counts and metrics"""
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)
        
        # Count by status
        status_counts = {'Done': 0, 'In Progress': 0, 'To Do': 0, 'Blocked': 0}
        by_assignee = {}
        by_project = {}
        by_issue_type = {}
        
        for issue in all_issues:
            # Status counting
            status = issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
            if status in status_counts:
                status_counts[status] += 1
            
            # Assignee counting
            assignee = issue.get('fields', {}).get('assignee', {})
            if assignee:
                assignee_name = assignee.get('displayName', 'Unknown')
                by_assignee[assignee_name] = by_assignee.get(assignee_name, 0) + 1
            
            # Project counting
            project = issue.get('fields', {}).get('project', {})
            if project:
                project_key = project.get('key', 'Unknown')
                by_project[project_key] = by_project.get(project_key, 0) + 1
            
            # Issue type counting
            issue_type = issue.get('fields', {}).get('issuetype', {})
            if issue_type:
                type_name = issue_type.get('name', 'Unknown')
                by_issue_type[type_name] = by_issue_type.get(type_name, 0) + 1
        
        return AggregatedData(
            total_issues=len(all_issues),
            done_count=status_counts['Done'],
            in_progress_count=status_counts['In Progress'],
            to_do_count=status_counts['To Do'],
            blocked_count=status_counts['Blocked'],
            by_assignee=by_assignee,
            by_project=by_project,
            by_issue_type=by_issue_type,
            risks=[],  # Will be populated by _identify_risks
            oldest_tickets=sorted(all_issues, key=lambda x: x.get('fields', {}).get('created', ''))[:5],
            recently_updated=sorted(all_issues, key=lambda x: x.get('fields', {}).get('updated', ''), reverse=True)[:5]
        )
    
    def _identify_risks(self, results: List[QueryResult]) -> List[Dict[str, Any]]:
        """Identify risk indicators"""
        risks = []
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)
        
        # Find oldest open tickets
        open_issues = [issue for issue in all_issues 
                     if issue.get('fields', {}).get('status', {}).get('name') not in ['Done', 'Closed']]
        
        if open_issues:
            oldest_issues = sorted(open_issues, key=lambda x: x.get('fields', {}).get('created', ''))[:3]
            for issue in oldest_issues:
                created_date = issue.get('fields', {}).get('created', '')
                if created_date:
                    try:
                        # Handle both ISO format with and without timezone
                        if created_date.endswith('Z'):
                            created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        else:
                            created_dt = datetime.fromisoformat(created_date)
                        
                        # Ensure both datetimes are timezone-aware
                        if created_dt.tzinfo is None:
                            created_dt = created_dt.replace(tzinfo=timezone.utc)
                        
                        now = datetime.now(timezone.utc)
                        days_old = (now - created_dt).days
                        
                        if days_old > 30:  # More than 30 days old
                            risks.append({
                                'type': 'old_ticket',
                                'severity': 'high' if days_old > 60 else 'medium',
                                'issue_key': issue.get('key'),
                                'summary': issue.get('fields', {}).get('summary', ''),
                                'days_old': days_old,
                                'assignee': issue.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned')
                            })
                    except Exception as e:
                        # Skip issues with invalid date formats
                        continue
        
        # Find frequently updated tickets (potential blockers)
        frequently_updated = []
        for issue in all_issues:
            updated_count = len(issue.get('changelog', {}).get('histories', []))
            if updated_count > 10:  # More than 10 updates
                frequently_updated.append({
                    'type': 'frequent_updates',
                    'severity': 'medium',
                    'issue_key': issue.get('key'),
                    'summary': issue.get('fields', {}).get('summary', ''),
                    'update_count': updated_count,
                    'assignee': issue.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned')
                })
        
        risks.extend(frequently_updated[:3])  # Top 3 frequently updated
        
        return risks
    
    def _enrich_with_urls(self, results: List[QueryResult]) -> List[QueryResult]:
        """Enrich results with clickable JIRA URLs"""
        base_url = self.jira_client.cfg.base_url.rstrip('/')
        
        for result in results:
            for issue in result.issues:
                issue_key = issue.get('key')
                if issue_key:
                    issue['jira_url'] = f"{base_url}/browse/{issue_key}"
        
        return results
    
    def _generate_text_response(self, results: List[QueryResult], aggregated: AggregatedData, 
                               risks: List[Dict[str, Any]], original_query: str) -> str:
        """Generate human-readable text response"""
        response_parts = []
        
        # Direct answer based on query type
        if 'compare' in original_query.lower() or 'vs' in original_query.lower():
            response_parts.append(self._generate_comparison_response(results, aggregated))
        elif 'status' in original_query.lower() or 'sprint' in original_query.lower():
            response_parts.append(self._generate_status_response(aggregated))
        elif 'blocked' in original_query.lower():
            response_parts.append(self._generate_blocked_response(results, aggregated))
        else:
            response_parts.append(self._generate_general_response(results, aggregated))
        
        # Add risk alerts if any
        if risks:
            risk_text = self._generate_risk_alerts(risks)
            if risk_text:
                response_parts.append(risk_text)
        
        return '\n\n'.join(response_parts)
    
    def _generate_comparison_response(self, results: List[QueryResult], aggregated: AggregatedData) -> str:
        """Generate comparison response"""
        response = "**Comparison Results:**\n"
        
        for i, result in enumerate(results):
            if result.total_count > 0:
                response += f"\n**Set {i+1}:** {result.total_count} tickets\n"
                response += f"- Done: {aggregated.done_count}\n"
                response += f"- In Progress: {aggregated.in_progress_count}\n"
                response += f"- To Do: {aggregated.to_do_count}\n"
                
                # Show top assignees
                top_assignees = sorted(aggregated.by_assignee.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_assignees:
                    response += f"- Top contributors: {', '.join([f'{name} ({count})' for name, count in top_assignees])}\n"
        
        return response
    
    def _generate_status_response(self, aggregated: AggregatedData) -> str:
        """Generate status response"""
        response = f"**Current Status:**\n"
        response += f"- Total tickets: {aggregated.total_issues}\n"
        response += f"- Done: {aggregated.done_count}\n"
        response += f"- In Progress: {aggregated.in_progress_count}\n"
        response += f"- To Do: {aggregated.to_do_count}\n"
        response += f"- Blocked: {aggregated.blocked_count}\n"
        
        if aggregated.by_assignee:
            response += f"\n**By Assignee:**\n"
            for assignee, count in sorted(aggregated.by_assignee.items(), key=lambda x: x[1], reverse=True):
                response += f"- {assignee}: {count} tickets\n"
        
        return response
    
    def _generate_blocked_response(self, results: List[QueryResult], aggregated: AggregatedData) -> str:
        """Generate blocked tickets response"""
        blocked_issues = []
        for result in results:
            for issue in result.issues:
                status = issue.get('fields', {}).get('status', {}).get('name', '')
                if status.lower() in ['blocked', 'waiting']:
                    blocked_issues.append(issue)
        
        if not blocked_issues:
            return "No blocked tickets found."
        
        response = f"**Blocked Tickets ({len(blocked_issues)}):**\n"
        for issue in blocked_issues[:5]:  # Show top 5
            issue_key = issue.get('key')
            summary = issue.get('fields', {}).get('summary', '')
            assignee = issue.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned')
            response += f"- {issue_key}: {summary} (assigned to {assignee})\n"
        
        return response
    
    def _generate_general_response(self, results: List[QueryResult], aggregated: AggregatedData) -> str:
        """Generate general response"""
        total_issues = sum(result.total_count for result in results)
        
        response = f"**Found {total_issues} tickets:**\n"
        response += f"- Done: {aggregated.done_count}\n"
        response += f"- In Progress: {aggregated.in_progress_count}\n"
        response += f"- To Do: {aggregated.to_do_count}\n"
        response += f"- Blocked: {aggregated.blocked_count}\n"
        
        # Show recent examples
        if aggregated.recently_updated:
            response += f"\n**Recent Examples:**\n"
            for issue in aggregated.recently_updated[:3]:
                issue_key = issue.get('key')
                summary = issue.get('fields', {}).get('summary', '')
                status = issue.get('fields', {}).get('status', {}).get('name', '')
                response += f"- {issue_key}: {summary} ({status})\n"
        
        return response
    
    def _generate_risk_alerts(self, risks: List[Dict[str, Any]]) -> str:
        """Generate risk alerts"""
        if not risks:
            return ""
        
        response = "**⚠️ Risk Alerts:**\n"
        
        for risk in risks:
            if risk['type'] == 'old_ticket':
                severity_icon = "🔴" if risk['severity'] == 'high' else "🟡"
                response += f"{severity_icon} {risk['issue_key']} is {risk['days_old']} days old (assigned to {risk['assignee']})\n"
            elif risk['type'] == 'frequent_updates':
                response += f"🟡 {risk['issue_key']} has {risk['update_count']} updates (potential blocker)\n"
        
        return response
    
    def _generate_json_response(self, results: List[QueryResult], aggregated: AggregatedData, 
                               risks: List[Dict[str, Any]]) -> str:
        """Generate machine-readable JSON response"""
        json_data = {
            'summary': {
                'total_issues': aggregated.total_issues,
                'status_counts': {
                    'done': aggregated.done_count,
                    'in_progress': aggregated.in_progress_count,
                    'to_do': aggregated.to_do_count,
                    'blocked': aggregated.blocked_count
                },
                'by_assignee': aggregated.by_assignee,
                'by_project': aggregated.by_project,
                'by_issue_type': aggregated.by_issue_type
            },
            'risks': risks,
            'recent_tickets': [
                {
                    'key': issue.get('key'),
                    'summary': issue.get('fields', {}).get('summary'),
                    'status': issue.get('fields', {}).get('status', {}).get('name'),
                    'assignee': issue.get('fields', {}).get('assignee', {}).get('displayName'),
                    'url': issue.get('jira_url')
                }
                for issue in aggregated.recently_updated[:10]
            ],
            'execution_info': {
                'queries_executed': len(results),
                'total_execution_time_ms': sum(result.execution_time_ms for result in results),
                'jql_queries': [result.jql_used for result in results]
            }
        }
        
        return json.dumps(json_data, indent=2)
    
    def _validate_response(self, response: str, original_query: str) -> str:
        """Validate response and auto-reprompt if needed"""
        response_lower = response.lower()
        
        # Check for required elements
        has_ticket_ids = bool(re.search(r'\b[A-Z]{2,}-\d+\b', response))
        has_counts = bool(re.search(r'\b\d+\b', response))
        has_statuses = any(status in response_lower for status in ['done', 'in progress', 'to do', 'blocked'])
        
        # If missing critical elements, try to enhance response
        if not has_ticket_ids or not has_counts or not has_statuses:
            enhanced_response = self._enhance_response(response, original_query)
            if enhanced_response != response:
                return enhanced_response
        
        return response
    
    def _enhance_response(self, response: str, original_query: str) -> str:
        """Enhance response with missing elements"""
        # This would typically involve re-prompting the LLM with specific instructions
        # For now, we'll add a note about missing data
        enhancement_note = "\n\n*Note: Some specific ticket details may not be available in the current data.*"
        return response + enhancement_note
    
    def _get_recent_context(self) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return self.conversation_memory[-5:] if self.conversation_memory else []
    
    async def _get_current_sprint_id(self) -> Optional[str]:
        """Get current sprint ID with caching"""
        # Check cache first
        if self.current_sprint_cache and self.cache_timestamp:
            if datetime.now() - self.cache_timestamp < timedelta(minutes=30):
                return self.current_sprint_cache
        
        try:
            # Get active sprints
            sprints = await self.jira_client.get_active_sprints()
            if sprints:
                # Find current sprint (active and not closed)
                for sprint in sprints:
                    if sprint.get('state') == 'active':
                        self.current_sprint_cache = str(sprint.get('id'))
                        self.cache_timestamp = datetime.now()
                        return self.current_sprint_cache
            
            return None
        except Exception as e:
            logger.error(f"Failed to get current sprint: {e}")
            return None
