"""
Intelligent AI Engine for Natural Language to Jira Query Processing
Uses OpenAI to understand user intent and generate appropriate responses
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
import re

logger = logging.getLogger(__name__)

class IntelligentAIEngine:
    """
    Advanced AI engine that uses OpenAI to:
    1. Understand natural language queries
    2. Generate appropriate JQL queries
    3. Provide contextual, varied responses
    4. Learn from conversation context
    """
    
    def __init__(self, jira_client):
        self.jira_client = jira_client
        self.client = None
        self.conversation_context = []
        self.last_query_context = {}
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("sk-your-actual"):
            self.client = OpenAI(api_key=api_key)
            logger.info("Intelligent AI Engine initialized with OpenAI")
        else:
            self.client = None
            if not api_key:
                logger.warning("No OpenAI API key found - AI features will be limited. Set OPENAI_API_KEY in backend/config.env")
            else:
                logger.warning("OpenAI API key is placeholder - AI features will be limited. Update OPENAI_API_KEY in backend/config.env")
    
    def add_context(self, user_query: str, jql: str, results: List[Dict], response: str):
        """Add conversation context for future reference"""
        context = {
            "user_query": user_query,
            "jql": jql,
            "result_count": len(results),
            "response": response,
            "timestamp": "now"
        }
        self.conversation_context.append(context)
        
        # Keep only last 10 interactions
        if len(self.conversation_context) > 10:
            self.conversation_context.pop(0)
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point - processes user query intelligently
        Returns: {
            "jql": "generated JQL",
            "response": "natural language response",
            "data": [...results...],
            "intent": "detected intent"
        }
        """
        if not self.client:
            return await self._fallback_processing(user_query)
        
        try:
            # Step 1: Understand the query and generate JQL
            query_analysis = await self._analyze_query(user_query)
            
            # Step 2: Execute JQL(s) - handle both single and multiple queries
            if isinstance(query_analysis["jql"], list):
                # Comparison query - execute multiple JQLs
                all_results = []
                jql_list = query_analysis["jql"]
                
                for i, jql in enumerate(jql_list):
                    try:
                        jql_result = await self._execute_jql(jql, query_analysis.get("intent"))
                        # Handle both old format (list) and new format (dict with results)
                        if isinstance(jql_result, dict) and 'results' in jql_result:
                            results = jql_result['results']
                            total_count = jql_result.get('total_count', len(results))
                        else:
                            results = jql_result if isinstance(jql_result, list) else []
                            total_count = len(results)
                        
                        all_results.append({
                            "entity": query_analysis.get("entities", {}).get(f"entity{i+1}", f"Entity {i+1}"),
                            "jql": jql,
                            "results": results,
                            "count": total_count,
                            "retrieved_count": jql_result.get('retrieved_count', len(results)) if isinstance(jql_result, dict) else len(results)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to execute JQL {i+1}: {jql}, error: {e}")
                        all_results.append({
                            "entity": query_analysis.get("entities", {}).get(f"entity{i+1}", f"Entity {i+1}"),
                            "jql": jql,
                            "results": [],
                            "count": 0,
                            "retrieved_count": 0,
                            "error": str(e)
                        })
                
                # Step 3: Generate comparison response
                response = await self._generate_comparison_response(user_query, query_analysis, all_results)
                
                # Step 4: Add to context
                combined_jql = " | ".join(jql_list)
                flat_results = []
                for result_set in all_results:
                    flat_results.extend(result_set["results"])
                self.add_context(user_query, combined_jql, flat_results, response)
                
                return {
                    "jql": combined_jql,
                    "response": response,
                    "data": all_results,
                    "intent": query_analysis["intent"],
                    "success": True,
                    "comparison_data": all_results
                }
            else:
                # Single query - original flow
                jql_result = await self._execute_jql(query_analysis["jql"], query_analysis.get("intent"))
                # Handle both old format (list) and new format (dict with results)
                if isinstance(jql_result, dict) and 'results' in jql_result:
                    results = jql_result['results']
                    total_count = jql_result.get('total_count', len(results))
                else:
                    results = jql_result if isinstance(jql_result, list) else []
                    total_count = len(results)
            
            # Step 3: Generate intelligent response
            retrieved_count = jql_result.get('retrieved_count') if isinstance(jql_result, dict) else None
            response = await self._generate_response(user_query, query_analysis, results, total_count, retrieved_count)
            
            # Step 4: Add to context
            self.add_context(user_query, query_analysis["jql"], results, response)
            
            return {
                "jql": query_analysis["jql"],
                "response": response,
                "data": results,
                "intent": query_analysis["intent"],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return await self._fallback_processing(user_query)
    
    async def _analyze_query(self, user_query: str) -> Dict[str, Any]:
        """Use OpenAI to understand the query and generate appropriate JQL"""
        
        # Get available projects and assignees for context
        projects = await self.jira_client.get_projects()
        project_keys = [p.get('key', '') for p in projects]
        
        # Get recent conversation context
        context_str = ""
        if self.conversation_context:
            recent_context = self.conversation_context[-3:]  # Last 3 interactions
            context_str = "\n".join([
                f"Previous: '{ctx['user_query']}' -> JQL: {ctx['jql']}" 
                for ctx in recent_context
            ])
        
        system_prompt = f"""You are an expert Jira JQL generator and query analyst. 

Available Jira Projects: {', '.join(project_keys)}

Your task is to:
1. Understand the user's natural language query
2. Generate appropriate JQL syntax
3. Identify the query intent and type

Recent conversation context:
{context_str}

Rules for JQL generation:
- Use exact project keys: {', '.join(project_keys)}
- For assignee queries, use displayName in quotes: assignee = "John Doe"
- For project queries, use: project = "CCM"
- For status: status = "To Do" or status = "Done"
- For issue types: issuetype = "Story" or issuetype = "Bug"
- Always quote string values
- Use ORDER BY updated DESC for lists
- For counts, don't use ORDER BY

CRITICAL - For comparative queries:
- Detect comparison words: "vs", "versus", "compare", "who's busier", "which has more", "between"
- For comparisons, generate MULTIPLE separate JQL queries
- Return array of JQLs to fetch data for each entity separately
- IMPORTANT: For person comparisons (assignee comparisons), search ACROSS ALL PROJECTS unless specifically mentioned
- For project comparisons, search within each specific project

Intent types:
- "project_overview": General project information
- "assignee_work": What someone is working on
- "issue_details": Specific ticket information
- "reporter_details": Information about who reported an issue
- "priority_details": Information about issue priority
- "status_details": Information about issue status
- "date_details": Information about creation/update dates
- "type_details": Information about issue type
- "assignee_comparison": Comparing assignees/people
- "project_comparison": Comparing projects
- "list_items": List specific items
- "count_items": Count of items
- "status_breakdown": Status analysis

For SINGLE entity queries, respond with:
{{
    "intent": "detected_intent_type",
    "jql": "single JQL query",
    "response_type": "count|list|breakdown",
    "entities": {{
        "project": "extracted project",
        "assignee": "extracted assignee",
        "issue_type": "extracted issue type",
        "status": "extracted status"
    }}
}}

For COMPARISON queries, respond with:
{{
    "intent": "assignee_comparison|project_comparison",
    "jql": ["query for entity 1", "query for entity 2"],
    "response_type": "comparison",
    "entities": {{
        "entity1": "first entity name",
        "entity2": "second entity name",
        "comparison_type": "assignee|project"
    }}
}}

Examples:
- "Who's busier: Ashwin Thyagarajan or SARAVANAN NP?" -> Multiple JQLs: assignee = "Ashwin Thyagarajan" | assignee = "SARAVANAN NP"
- "Which project has more urgent work: CCM or CES?" -> Multiple JQLs: project = "CCM" | project = "CES"
- "Compare CCM vs TI projects" -> Multiple JQLs: project = "CCM" | project = "TI"
- "Who resolves bugs faster: Ashwin or Saravanan?" -> Multiple JQLs: assignee = "Ashwin" AND issuetype = "Bug" | assignee = "Saravanan" AND issuetype = "Bug"
- "Who is the reporter of CCM-283?" -> Single JQL: issue = "CCM-283"
- "CCM-283 details" -> Single JQL: issue = "CCM-283"
- "What is the priority of CCM-283?" -> Single JQL: issue = "CCM-283"
- "What is the status of CCM-283?" -> Single JQL: issue = "CCM-283"
- "When was CCM-283 created?" -> Single JQL: issue = "CCM-283"
- "What type is CCM-283?" -> Single JQL: issue = "CCM-283"
"""

        user_prompt = f"""Query: "{user_query}"

Generate appropriate JQL and analyze the intent."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            raw_response = response.choices[0].message.content.strip()
            logger.info(f"Raw OpenAI response: {raw_response}")
            
            result = json.loads(raw_response)
            logger.info(f"AI Analysis: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            # Enhanced fallback analysis
            query_lower = user_query.lower()
            
            # Detect specific issue keys (e.g., CCM-283, CES-123)
            import re
            issue_key_pattern = r'\b([A-Z]{2,}-\d+)\b'
            issue_key_match = re.search(issue_key_pattern, user_query, re.IGNORECASE)
            specific_issue_key = issue_key_match.group(1) if issue_key_match else None
            
            if specific_issue_key:
                return {
                    "intent": "issue_details",
                    "jql": f'issue = "{specific_issue_key}"',
                    "response_type": "list",
                    "entities": {"issue_key": specific_issue_key}
                }
            else:
                # Fallback to simple analysis
                return {
                    "intent": "general_query",
                    "jql": f'project in ({", ".join(project_keys)}) ORDER BY updated DESC',
                    "response_type": "list",
                    "entities": {}
                }
    
    async def _execute_jql(self, jql: str, query_intent: str = None) -> Dict[str, Any]:
        """
        Execute JQL with hybrid logic based on query intent:
        - count_items: Return only total count using maxResults=0
        - breakdown/overview: Fetch ALL issues using pagination for analysis
        """
        try:
            # Determine if this is a count-only query
            is_count_only = (
                query_intent == "count_items" or 
                query_intent == "story_count" or
                query_intent == "issue_count" or
                "count" in jql.lower() or 
                "group by" in jql.lower()
            )
            
            if is_count_only:
                # For count-only queries, use maxResults=0 to get only the total count
                logger.info(f"Executing count-only query: {jql}")
                search_result = await self.jira_client.search(jql, max_results=0)
                
                if isinstance(search_result, dict):
                    total_count = search_result.get('total', 0)
                    logger.info(f"Count query result: {total_count} total items")
                    return {
                        'results': [],
                        'total_count': total_count,
                        'retrieved_count': 0,
                        'is_count_only': True
                    }
                else:
                    logger.warning(f"Unexpected count result format: {type(search_result)}")
                    return {
                        'results': [],
                        'total_count': 0,
                        'retrieved_count': 0,
                        'is_count_only': True
                    }
            else:
                # For breakdown/overview queries, fetch ALL issues using pagination
                logger.info(f"Executing breakdown query with full pagination: {jql}")
                
                # Enhanced field list for better data quality
                enhanced_fields = [
                    'key', 'summary', 'status', 'assignee', 'priority', 'issuetype',
                    'project', 'created', 'updated', 'description', 'reporter',
                    'labels', 'components', 'fixVersions', 'duedate'
                ]
                
                # Get all results with pagination to ensure we don't miss any issues
                all_issues = []
                start_at = 0
                max_results_per_page = 100  # Increased for better efficiency
                total_count_from_api = None
                
                while True:
                    search_result = await self.jira_client.search(
                        jql, 
                        max_results=max_results_per_page, 
                        fields=enhanced_fields,
                        start_at=start_at
                    )
                    
                    # Extract issues from the Jira response structure
                    if isinstance(search_result, dict) and 'issues' in search_result:
                        issues = search_result['issues']
                        # Get total count from first page response
                        if total_count_from_api is None:
                            total_count_from_api = search_result.get('total', 0)
                        
                        # Check for pagination using total count and current position
                        has_more_pages = (start_at + len(issues)) < total_count_from_api
                        logger.info(f"Page {start_at//max_results_per_page + 1}: Found {len(issues)} issues, Total: {total_count_from_api}, Has more: {has_more_pages}")
                    elif isinstance(search_result, list):
                        issues = search_result
                        has_more_pages = False  # List format doesn't support pagination
                        total_count_from_api = len(issues)
                        logger.info(f"Page {start_at//max_results_per_page + 1}: Found {len(issues)} issues (list format)")
                    else:
                        logger.error(f"Unexpected search result format: {type(search_result)}")
                        break
                    
                    if not issues:
                        break
                    
                    all_issues.extend(issues)
                    
                    # Break if we've retrieved all available issues
                    if not has_more_pages or len(issues) < max_results_per_page:
                        logger.info(f"Breaking pagination: has_more_pages={has_more_pages}, current_page_size={len(issues)}, max_per_page={max_results_per_page}")
                        break
                    
                    start_at += max_results_per_page
                
                logger.info(f"Retrieved {len(all_issues)} total issues using pagination (API total: {total_count_from_api})")
                
                # Filter out items with missing essential data
                filtered_results = []
                for issue in all_issues:
                    key = issue.get('key', 'UNKNOWN')
                    fields = issue.get('fields', {})
                    summary = fields.get('summary', '') if fields else ''
                    
                    # Skip items with no key or summary unless it's a specific key lookup
                    if key == 'UNKNOWN' and not summary:
                        logger.warning(f"Skipping item with missing key/summary: {issue}")
                        continue
                    
                    filtered_results.append(issue)
                
                logger.info(f"Processed {len(filtered_results)} valid issues from {len(all_issues)} total")
                
                # Return both results and accurate counts for analysis
                # total_count_from_api = true Jira count, len(filtered_results) = fetched count
                return {
                    'results': filtered_results,
                    'total_count': total_count_from_api or len(filtered_results),  # True Jira count
                    'retrieved_count': len(filtered_results),  # Actually fetched count
                    'is_count_only': False
                }
                
        except Exception as e:
            logger.error(f"JQL execution failed: {e}")
            return {
                'results': [],
                'total_count': 0,
                'retrieved_count': 0,
                'is_count_only': False,
                'error': str(e)
            }
    
    async def _generate_response(self, user_query: str, query_analysis: Dict, results: List[Dict], total_count: int = None, retrieved_count: int = None) -> str:
        """Generate intelligent, contextual response"""
        
        if not self.client:
            return self._basic_response(query_analysis, results)
        
        # Check if this is a specific issue query and extract reporter context
        specific_issue_context = None
        if len(results) == 1 and results[0].get('key'):
            issue = results[0]
            fields = issue.get('fields', {})
            reporter = fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown'
            specific_issue_context = {
                'issue_key': issue.get('key'),
                'reporter': reporter,
                'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                'status': fields.get('status', {}).get('name', 'Unknown') if fields.get('status') else 'Unknown'
            }
        
        # Prepare data summary for AI
        if not results:
            data_summary = "No matching items found."
        elif len(results) == 1 and "count" in results[0]:
            data_summary = f"Found {results[0]['count']} total items."
        else:
            # Analyze the results and create comprehensive summary
            data_summary = self._create_detailed_analysis(results, user_query, total_count, retrieved_count, specific_issue_context)
            
            if len(results) > 5:
                data_summary += f"... and {len(results) - 5} more items."
        
        system_prompt = """You are an intelligent Jira leadership assistant that provides strategic insights and actionable recommendations.

Your Role:
- Act as a strategic advisor to engineering managers and leadership teams
- Provide contextual analysis, not just raw data
- Identify patterns, risks, and opportunities in project data
- Give actionable recommendations for team management and project success

Response Guidelines:
- Start with a clear, direct answer to the question
- Provide strategic context and implications
- Include specific recommendations when relevant
- Use leadership-friendly language and metrics
- Highlight potential risks or blockers
- Suggest next steps or follow-up actions
- Be concise but comprehensive

For specific query types:
- Single issues: Analyze priority, assignee workload, reporter details, status, dates, and project impact
- Reporter queries: When asked about a specific issue's reporter, FIRST identify who the reporter is, THEN analyze their workload and patterns. Be specific to the issue being discussed.
- Priority queries: Analyze priority distribution, escalation patterns, and impact on delivery
- Status queries: Provide current status, status history, and workflow progression
- Date queries: Analyze creation patterns, update frequency, and resolution timelines
- Type queries: Analyze issue type distribution and workload patterns
- Project comparisons: Compare velocity, team size, defect ratios, and resource needs
- Team queries: Assess workload distribution, capacity, and performance patterns
- Story/count queries: Provide exact counts, assignee breakdowns, and workload analysis
- Assignee analysis: Detail individual contributions, capacity, and task distribution

When data shows counts and breakdowns:
- Always mention exact story counts and totals
- Highlight assignee workload distribution (who has how many items)
- Include reporter information when relevant to the query
- Identify potential bottlenecks or uneven workload distribution
- Provide specific recommendations for workload balancing
- Call out any assignees with unusually high or low task counts

CRITICAL: When analyzing reporters:
- If the user asks about a specific issue's reporter, start by confirming "X is the reporter of [issue]"
- Then analyze that specific reporter's workload and patterns
- Do NOT give general reporter breakdowns unless specifically asked for all reporters
- Focus on the specific reporter mentioned in the context

Always provide actionable insights that help leaders make informed decisions."""

        user_prompt = f"""User asked: "{user_query}"

Query intent: {query_analysis.get('intent', 'unknown')}
JQL executed: {query_analysis.get('jql', 'N/A')}

Data found:
{data_summary}

Provide a natural, helpful response that directly answers their question."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # Higher temperature for more varied responses
                max_tokens=1000  # Increased for longer, more complete responses
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self._basic_response(query_analysis, results)
    
    def _basic_response(self, query_analysis: Dict, results: List[Dict]) -> str:
        """Fallback response when OpenAI is not available"""
        if not results:
            return "No matching items found."
        
        if len(results) == 1 and "count" in results[0]:
            count = results[0]["count"]
            return f"Found {count} matching items."
        
        return f"Found {len(results)} items matching your criteria."
    
    async def _fallback_processing(self, user_query: str) -> Dict[str, Any]:
        """Enhanced fallback when OpenAI is not available"""
        try:
            # Get available projects
            projects = await self.jira_client.get_projects()
            project_keys = [p.get('key', '') for p in projects]
        
            # Enhanced keyword-based processing
            query_lower = user_query.lower()
            
            # Detect specific issue keys (e.g., CCM-283, CES-123)
            import re
            issue_key_pattern = r'\b([A-Z]{2,}-\d+)\b'
            issue_key_match = re.search(issue_key_pattern, user_query, re.IGNORECASE)
            specific_issue_key = issue_key_match.group(1) if issue_key_match else None
            
            # Detect specific project mentions
            mentioned_project = None
            for project in projects:
                if project.get('key', '').lower() in query_lower:
                    mentioned_project = project.get('key', '')
                    break
            
            # Detect specific issue types
            issue_type = None
            if any(word in query_lower for word in ['story', 'stories', 'user story']):
                issue_type = 'Story'
            elif any(word in query_lower for word in ['bug', 'bugs', 'defect', 'defects']):
                issue_type = 'Bug'
            elif any(word in query_lower for word in ['task', 'tasks']):
                issue_type = 'Task'
            
            # Detect assignee mentions
            assignee = None
            if 'ashwin' in query_lower:
                assignee = 'Ashwin Thyagarajan'
            elif 'ashwini' in query_lower:
                assignee = 'Ashwini Kumar'
            
            # Build JQL based on detected entities
            jql_parts = []
            
            if specific_issue_key:
                # Specific issue query
                jql_parts.append(f'issue = "{specific_issue_key}"')
            elif mentioned_project:
                jql_parts.append(f'project = "{mentioned_project}"')
            elif project_keys:
                project_list = ", ".join([f'"{k}"' for k in project_keys])
                jql_parts.append(f'project in ({project_list})')
            
            if issue_type:
                jql_parts.append(f'issuetype = "{issue_type}"')
            
            if assignee:
                jql_parts.append(f'assignee = "{assignee}"')
            
            # Detect status queries
            if any(word in query_lower for word in ['open', 'to do', 'in progress']):
                jql_parts.append('status != "Done"')
            elif 'done' in query_lower or 'completed' in query_lower:
                jql_parts.append('status = "Done"')
            
            if jql_parts:
                jql = ' AND '.join(jql_parts)
            else:
                project_list = ", ".join([f'"{k}"' for k in project_keys])
                jql = f'project in ({project_list})'
            
            # Only add ORDER BY for non-specific issue queries
            if not specific_issue_key:
                jql += ' ORDER BY updated DESC'
            
            # Execute query
            jql_result = await self._execute_jql(jql, "enhanced_fallback")
            # Handle both old format (list) and new format (dict with results)
            if isinstance(jql_result, dict) and 'results' in jql_result:
                results = jql_result['results']
            else:
                results = jql_result if isinstance(jql_result, list) else []
            
            # Generate enhanced response
            response = self._enhanced_fallback_response(user_query, specific_issue_key, mentioned_project, issue_type, assignee, results)
            
            return {
                "jql": jql,
                "response": response,
                "data": results,
                "intent": "enhanced_fallback",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Enhanced fallback processing failed: {e}")
            return {
                "jql": "",
                "response": f"I apologize, but I encountered an error processing your request: {str(e)}. Please try rephrasing your question.",
                "data": [],
                "intent": "error",
                "success": False
            }
    
    def _enhanced_fallback_response(self, user_query: str, specific_issue_key: str, project: str, issue_type: str, assignee: str, results: List[Dict]) -> str:
        """Generate enhanced fallback response"""
        if not results:
            return "I couldn't find any matching items. Try being more specific about the project, assignee, or issue type."
        
        # Count different types
        stories = sum(1 for r in results if r.get('fields', {}).get('issuetype', {}).get('name', '') == 'Story')
        bugs = sum(1 for r in results if r.get('fields', {}).get('issuetype', {}).get('name', '') in ['Bug', 'Defect'])
        tasks = sum(1 for r in results if r.get('fields', {}).get('issuetype', {}).get('name', '') == 'Task')
        
        response_parts = []
        
        # Context-aware introduction
        if specific_issue_key:
            response_parts.append(f"Here are the details for {specific_issue_key}:")
        elif assignee:
            response_parts.append(f"Here's what I found for {assignee}:")
        elif project:
            response_parts.append(f"Here's what I found in the {project} project:")
        elif issue_type:
            response_parts.append(f"Here are the {issue_type.lower()}s I found:")
        else:
            response_parts.append("Here's what I found:")
        
        # Summary
        total = len(results)
        if total == 1:
            item = results[0]
            key = item.get('key', '')
            summary = item.get('fields', {}).get('summary', 'No summary')
            status = item.get('fields', {}).get('status', {}).get('name', 'Unknown')
            assignee_name = item.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned')
            
            response_parts.extend([
                f"\n**{key}: {summary}**",
                f"Status: {status}",
                f"Assignee: {assignee_name}",
                f"Priority: {item.get('fields', {}).get('priority', {}).get('name', 'Unknown')}",
                f"\nLeadership note: {assignee_name} owns this {item.get('fields', {}).get('issuetype', {}).get('name', 'item').lower()} currently to do. Priority is {item.get('fields', {}).get('priority', {}).get('name', 'unknown').lower()}."
            ])
        else:
            response_parts.append(f"\nFound {total} items:")
            if stories > 0:
                response_parts.append(f"• {stories} stories")
            if bugs > 0:
                response_parts.append(f"• {bugs} bugs")
            if tasks > 0:
                response_parts.append(f"• {tasks} tasks")
            
            # Show first few items
            for i, item in enumerate(results[:3]):
                key = item.get('key', '')
                summary = item.get('fields', {}).get('summary', 'No summary')
                status = item.get('fields', {}).get('status', {}).get('name', 'Unknown')
                assignee_name = item.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned')
                
                response_parts.append(f"\n**{key}**: {summary}")
                response_parts.append(f"Status: {status} | Assignee: {assignee_name}")
            
            if total > 3:
                response_parts.append(f"\n...and {total - 3} more items.")
        
        # Add note about OpenAI
        response_parts.append(f"\n💡 **Note**: For more intelligent responses and natural language processing, configure your OpenAI API key in backend/config.env")
        
        return "\n".join(response_parts)
    
    def _create_detailed_analysis(self, results: List[Dict], user_query: str, total_count: int = None, retrieved_count: int = None, specific_issue_context: Dict = None) -> str:
        """Create detailed analysis of Jira results with proper field extraction and accurate count reporting"""
        if not results:
            return "No items found."
        
        # Use provided counts or fall back to len(results)
        actual_total = total_count if total_count is not None else len(results)
        actual_retrieved = retrieved_count if retrieved_count is not None else len(results)
        
        # Extract and analyze data properly from Jira structure
        analysis = {
            'total_items': actual_total,
            'retrieved_items': actual_retrieved,
            'by_assignee': {},
            'by_reporter': {},
            'by_status': {},
            'by_type': {},
            'by_priority': {},
            'by_created_date': {},
            'by_updated_date': {},
            'items_list': [],
            'specific_issue_context': specific_issue_context
        }
        
        for item in results:
            # Extract fields properly from Jira structure
            key = item.get('key', 'UNKNOWN')
            fields = item.get('fields', {})
            
            summary = fields.get('summary', 'No summary')
            status = fields.get('status', {}).get('name', 'Unknown') if fields.get('status') else 'Unknown'
            issue_type = fields.get('issuetype', {}).get('name', 'Unknown') if fields.get('issuetype') else 'Unknown'
            priority = fields.get('priority', {}).get('name', 'Unknown') if fields.get('priority') else 'Unknown'
            assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'
            reporter = fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown'
            
            # Extract dates
            created_date = fields.get('created', 'Unknown')
            updated_date = fields.get('updated', 'Unknown')
            resolution_date = fields.get('resolutiondate', 'Not resolved')
            
            # Extract project information
            project = fields.get('project', {}).get('name', 'Unknown') if fields.get('project') else 'Unknown'
            project_key = fields.get('project', {}).get('key', 'Unknown') if fields.get('project') else 'Unknown'
            
            # Extract labels and components
            labels = fields.get('labels', [])
            components = [comp.get('name', 'Unknown') for comp in fields.get('components', [])]
            
            # Extract story points if available
            story_points = fields.get('customfield_10016', 'Not estimated')  # Common story points field
            
            # Extract fix versions
            fix_versions = [version.get('name', 'Unknown') for version in fields.get('fixVersions', [])]
            
            # Count by assignee
            if assignee not in analysis['by_assignee']:
                analysis['by_assignee'][assignee] = 0
            analysis['by_assignee'][assignee] += 1
            
            # Count by reporter
            if reporter not in analysis['by_reporter']:
                analysis['by_reporter'][reporter] = 0
            analysis['by_reporter'][reporter] += 1
            
            # Count by status
            if status not in analysis['by_status']:
                analysis['by_status'][status] = 0
            analysis['by_status'][status] += 1
            
            # Count by type
            if issue_type not in analysis['by_type']:
                analysis['by_type'][issue_type] = 0
            analysis['by_type'][issue_type] += 1
            
            # Count by priority
            if priority not in analysis['by_priority']:
                analysis['by_priority'][priority] = 0
            analysis['by_priority'][priority] += 1
            
            # Count by created date (group by month)
            if created_date != 'Unknown':
                try:
                    from datetime import datetime
                    created_month = datetime.fromisoformat(created_date.replace('Z', '+00:00')).strftime('%Y-%m')
                    if created_month not in analysis['by_created_date']:
                        analysis['by_created_date'][created_month] = 0
                    analysis['by_created_date'][created_month] += 1
                except:
                    pass
            
            # Count by updated date (group by month)
            if updated_date != 'Unknown':
                try:
                    from datetime import datetime
                    updated_month = datetime.fromisoformat(updated_date.replace('Z', '+00:00')).strftime('%Y-%m')
                    if updated_month not in analysis['by_updated_date']:
                        analysis['by_updated_date'][updated_month] = 0
                    analysis['by_updated_date'][updated_month] += 1
                except:
                    pass
            
            # Add to items list
            analysis['items_list'].append({
                'key': key,
                'summary': summary,
                'status': status,
                'type': issue_type,
                'priority': priority,
                'assignee': assignee,
                'reporter': reporter,
                'created_date': created_date,
                'updated_date': updated_date,
                'resolution_date': resolution_date,
                'project': project,
                'project_key': project_key,
                'labels': labels,
                'components': components,
                'story_points': story_points,
                'fix_versions': fix_versions
            })
        
        # Create comprehensive summary
        summary_parts = []
        
        # Add specific issue context if available (for reporter queries)
        if specific_issue_context and specific_issue_context.get('issue_key') and specific_issue_context.get('reporter'):
            summary_parts.append(f"**{specific_issue_context['reporter']} is the reporter of {specific_issue_context['issue_key']}.**")
            summary_parts.append("")
        
        # Show accurate count information in the requested format
        if actual_total == actual_retrieved:
            summary_parts.append(f"Found {analysis['total_items']} total items (complete dataset analyzed):")
        else:
            summary_parts.append(f"Showing segregations for {analysis['retrieved_items']} issues (out of {analysis['total_items']} total).")
        
        # Add type breakdown
        if analysis['by_type']:
            summary_parts.append("\n**Issue Type Breakdown:**")
            for issue_type, count in sorted(analysis['by_type'].items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"- {issue_type}: {count}")
        
        # Add assignee breakdown
        if analysis['by_assignee']:
            summary_parts.append("\n**Assignee Breakdown:**")
            for assignee, count in sorted(analysis['by_assignee'].items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"- {assignee}: {count} items")
        
        # Add reporter breakdown
        if analysis['by_reporter']:
            summary_parts.append("\n**Reporter Breakdown:**")
            for reporter, count in sorted(analysis['by_reporter'].items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"- {reporter}: {count} items")
        
        # Add status breakdown
        if analysis['by_status']:
            summary_parts.append("\n**Status Breakdown:**")
            for status, count in sorted(analysis['by_status'].items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"- {status}: {count}")
        
        # Add priority breakdown
        if analysis['by_priority']:
            summary_parts.append("\n**Priority Breakdown:**")
            for priority, count in sorted(analysis['by_priority'].items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"- {priority}: {count}")
        
        # Add created date breakdown
        if analysis['by_created_date']:
            summary_parts.append("\n**Created Date Breakdown:**")
            for date, count in sorted(analysis['by_created_date'].items(), reverse=True):
                summary_parts.append(f"- {date}: {count}")
        
        # Add updated date breakdown
        if analysis['by_updated_date']:
            summary_parts.append("\n**Updated Date Breakdown:**")
            for date, count in sorted(analysis['by_updated_date'].items(), reverse=True):
                summary_parts.append(f"- {date}: {count}")
        
        # Add sample items
        summary_parts.append("\n**Sample Items:**")
        for i, item in enumerate(analysis['items_list'][:5]):
            summary_parts.append(f"- {item['key']}: {item['summary']}")
            summary_parts.append(f"  Status: {item['status']} | Priority: {item['priority']} | Type: {item['type']}")
            summary_parts.append(f"  Assignee: {item['assignee']} | Reporter: {item['reporter']}")
            if item['created_date'] != 'Unknown':
                summary_parts.append(f"  Created: {item['created_date'][:10]} | Updated: {item['updated_date'][:10]}")
            if item['story_points'] != 'Not estimated':
                summary_parts.append(f"  Story Points: {item['story_points']}")
            summary_parts.append("")
        
        if len(analysis['items_list']) > 5:
            summary_parts.append(f"... and {len(analysis['items_list']) - 5} more items.")
        
        return "\n".join(summary_parts)
    
    async def _generate_comparison_response(self, user_query: str, query_analysis: Dict[str, Any], all_results: List[Dict]) -> str:
        """Generate comparison response using OpenAI"""
        try:
            # Prepare comparison data summary
            comparison_summary = []
            
            for result_set in all_results:
                entity = result_set["entity"]
                count = result_set["count"]
                results = result_set["results"]
                
                if result_set.get("error"):
                    comparison_summary.append(f"{entity}: Error - {result_set['error']}")
                    continue
                
                # Analyze the results for this entity
                if results:
                    retrieved_count = result_set.get('retrieved_count', len(results))
                    entity_analysis = self._create_detailed_analysis(results, f"{entity} analysis", count, retrieved_count)
                    comparison_summary.append(f"{entity}: {count} items\n{entity_analysis}")
                else:
                    comparison_summary.append(f"{entity}: 0 items (no data found)")
            
            comparison_data = "\n\n---\n\n".join(comparison_summary)
            
            # Generate comparison response using OpenAI
            system_prompt = """You are an intelligent Jira leadership assistant that provides strategic insights and actionable recommendations for comparative analysis.

When comparing entities (people, projects, etc.), provide:
1. Clear comparison summary with exact numbers
2. Winner/leader identification
3. Key differences and insights
4. Strategic recommendations
5. Workload balance analysis (for people)
6. Resource allocation suggestions (for projects)

Format your response as:
🔍 **Comparison Analysis**
📊 **Key Metrics**
💡 **Strategic Insights**
🎯 **Recommendations**

Be specific, actionable, and leadership-focused."""

            user_prompt = f"""User asked: "{user_query}"

Comparison data:
{comparison_data}

Provide a comprehensive comparison analysis with strategic insights and clear recommendations."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating comparison response: {e}")
            # Fallback to simple comparison
            return self._fallback_comparison_response(user_query, all_results)
    
    def _fallback_comparison_response(self, user_query: str, all_results: List[Dict]) -> str:
        """Fallback comparison response when OpenAI fails"""
        try:
            response_parts = ["🔍 **Comparison Analysis**", ""]
            
            # Extract entities and counts
            entities_data = []
            for result_set in all_results:
                entity = result_set["entity"]
                count = result_set["count"]
                entities_data.append((entity, count))
            
            # Sort by count (descending)
            entities_data.sort(key=lambda x: x[1], reverse=True)
            
            # Summary
            response_parts.append("📊 **Results Summary:**")
            for entity, count in entities_data:
                response_parts.append(f"- **{entity}**: {count} items")
            
            response_parts.append("")
            
            # Determine winner
            if len(entities_data) >= 2:
                winner_entity, winner_count = entities_data[0]
                runner_up_entity, runner_up_count = entities_data[1]
                
                if winner_count > runner_up_count:
                    response_parts.append(f"🏆 **Winner**: {winner_entity} with {winner_count} items")
                    difference = winner_count - runner_up_count
                    response_parts.append(f"📈 **Difference**: {difference} more items than {runner_up_entity}")
                elif winner_count == runner_up_count:
                    response_parts.append(f"🤝 **Tied**: Both {winner_entity} and {runner_up_entity} have {winner_count} items")
                
                response_parts.append("")
            
            # Basic insights
            response_parts.append("💡 **Key Insights:**")
            total_items = sum(count for _, count in entities_data)
            if total_items > 0:
                for entity, count in entities_data:
                    percentage = (count / total_items) * 100
                    response_parts.append(f"- {entity} handles {percentage:.1f}% of the workload")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error in fallback comparison: {e}")
            return f"Comparison completed. Found data for {len(all_results)} entities."
