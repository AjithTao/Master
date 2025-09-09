"""
Advanced Query Processing Engine
Replaces basic keyword matching with intelligent semantic understanding
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from ai_engine import AdvancedAIEngine
from jira_client import JiraClient

class AdvancedQueryProcessor:
    """Advanced query processor with semantic understanding"""
    
    def __init__(self, ai_engine: AdvancedAIEngine, jira_client: Optional[JiraClient] = None):
        self.ai_engine = ai_engine
        self.jira_client = jira_client
        self.query_cache = {}
        self.entity_extractor = EntityExtractor()
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query with advanced AI understanding"""
        
        # Check cache first
        cache_key = query.lower().strip()
        if cache_key in self.query_cache:
            cached_result = self.query_cache[cache_key]
            if datetime.now() - cached_result['timestamp'] < timedelta(minutes=5):
                return cached_result['result']
        
        # Analyze query with AI
        intent_analysis = self.ai_engine.analyze_query_intent(query)
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(query)
        
        # Debug logging
        print(f"🔍 Query: {query}")
        print(f"🔍 Extracted entities: {entities}")
        print(f"🔍 Intent analysis: {intent_analysis}")
        print(f"🔍 Jira client available: {self.jira_client is not None}")
        print(f"🔍 AI engine available: {self.ai_engine is not None}")
        
        # Check if we have the required components
        if not self.jira_client:
            print("⚠️ No Jira client available - using AI-only mode")
            # Use AI engine directly for intelligent responses without Jira data
            try:
                response = self.ai_engine.generate_intelligent_response(query, {})
                return {
                    'type': 'ai_only',
                    'response': response,
                    'data': {},
                    'confidence': 0.8
                }
            except Exception as e:
                print(f"❌ AI-only mode failed: {e}")
                return {
                    'type': 'error',
                    'response': 'I can provide general insights, but Jira integration would give more specific data. What would you like to know?',
                    'data': {},
                    'confidence': 0.5
                }
        
        if not self.ai_engine:
            print("❌ No AI engine available!")
            return {
                'type': 'error', 
                'response': 'AI engine is not available.',
                'data': {},
                'confidence': 0.0
            }
        
        # Determine processing strategy
        processing_strategy = self._determine_processing_strategy(intent_analysis, entities)
        print(f"🔍 Processing strategy: {processing_strategy}")
        
        # Execute processing
        result = await self._execute_processing_strategy(query, processing_strategy, entities)
        
        # Cache result
        self.query_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        return result
    
    def _determine_processing_strategy(self, intent: Dict[str, Any], entities: Dict[str, List[str]]) -> str:
        """Determine the best processing strategy based on intent and entities"""
        
        primary_intent = intent.get('primary_intent', 'data_retrieval')
        complexity = intent.get('complexity_level', 'simple')
        
        if primary_intent == 'prediction':
            return 'predictive_analysis'
        elif primary_intent == 'recommendation':
            return 'recommendation_engine'
        elif primary_intent == 'comparison':
            return 'comparative_analysis'
        elif primary_intent == 'analysis':
            return 'deep_analysis'
        elif complexity == 'complex':
            return 'multi_step_analysis'
        else:
            return 'standard_processing'
    
    async def _execute_processing_strategy(self, query: str, strategy: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Execute the determined processing strategy"""
        
        if strategy == 'predictive_analysis':
            return await self._handle_predictive_analysis(query, entities)
        elif strategy == 'recommendation_engine':
            return await self._handle_recommendation_engine(query, entities)
        elif strategy == 'comparative_analysis':
            return await self._handle_comparative_analysis(query, entities)
        elif strategy == 'deep_analysis':
            return await self._handle_deep_analysis(query, entities)
        elif strategy == 'multi_step_analysis':
            return await self._handle_multi_step_analysis(query, entities)
        else:
            return await self._handle_standard_processing(query, entities)
    
    async def _handle_standard_processing(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Handle standard processing for simple queries"""
        
        # Get relevant data
        data = await self._get_standard_data(entities, query)
        
        # Generate response
        response = self.ai_engine.generate_intelligent_response(query, data)
        
        return {
            'type': 'standard',
            'response': response,
            'data': data,
            'confidence': 0.9,
            'follow_up_suggestions': []
        }
    
    async def _get_standard_data(self, entities: Dict[str, List[str]], query: str = "") -> Dict[str, Any]:
        """Get standard data for simple queries with enhanced Jira access"""
        
        if not self.jira_client:
            return {}
        
        # Get basic data based on entities
        if entities.get('tickets'):
            ticket_keys = entities['tickets']
            data = {}
            for ticket_key in ticket_keys:
                # Get detailed issue information
                issue_details = await self.jira_client.get_issue_details(ticket_key)
                if issue_details:
                    data[ticket_key] = {
                        'issue': issue_details,
                        'comments': await self.jira_client.get_issue_comments(ticket_key),
                        'transitions': await self.jira_client.get_issue_transitions(ticket_key)
                    }
            return data
        
        # Handle sprint-related queries
        if entities.get('sprints') or entities.get('timeframes'):
            return await self._get_sprint_data(entities)
        
        # Handle backlog queries
        if any(keyword in str(entities).lower() for keyword in ['backlog', 'pending', 'todo']):
            return await self._get_backlog_data(entities)
        
        # Handle project queries
        if entities.get('projects') or any(keyword in query.lower() for keyword in ['project', 'ccm', 'ces', 'gtms', 'ti']):
            return await self._get_project_data(entities, query)
        
        # Use intelligent JQL queries based on query patterns
        return await self._get_intelligent_jql_data(entities)
    
    async def _get_intelligent_jql_data(self, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Get data using intelligent JQL queries based on query patterns"""
        
        if not self.jira_client:
            return {}
        
        data = {}
        query_lower = str(entities).lower()
        
        # Recent issues (last 30 days)
        if any(keyword in query_lower for keyword in ['recent', 'last 30', 'past month', 'created recently']):
            jql = "created >= -30d ORDER BY created DESC"
            result = await self.jira_client.search(jql, max_results=100)
            data['recent_created'] = result.get('issues', [])
        
        # Recently updated issues
        if any(keyword in query_lower for keyword in ['updated', 'modified', 'changed', 'last week']):
            jql = "updated >= -1w ORDER BY updated DESC"
            result = await self.jira_client.search(jql, max_results=100)
            data['recently_updated'] = result.get('issues', [])
        
        # Recently resolved issues
        if any(keyword in query_lower for keyword in ['resolved', 'completed', 'done', 'finished']):
            jql = "resolutiondate >= -1w ORDER BY updated DESC"
            result = await self.jira_client.search(jql, max_results=100)
            data['recently_resolved'] = result.get('issues', [])
        
        # Issues by assignee (with proper account ID resolution)
        assignees = entities.get('assignees', [])
        if assignees:
            for assignee in assignees:
                jql = await self.jira_client.build_assignee_jql(assignee)
                result = await self.jira_client.search(jql, max_results=50)
                data[f'assignee_{assignee}'] = result.get('issues', [])
        
        # Stories by specific assignee
        if any(keyword in query_lower for keyword in ['story', 'stories']) and assignees:
            for assignee in assignees:
                assignee_jql = await self.jira_client.build_assignee_jql(assignee)
                jql = f"issuetype = Story AND {assignee_jql} ORDER BY created DESC"
                result = await self.jira_client.search(jql, max_results=50)
                data[f'stories_{assignee}'] = result.get('issues', [])
        
        # High priority bugs
        if any(keyword in query_lower for keyword in ['bug', 'bugs', 'highest priority', 'critical']):
            jql = "priority = Highest AND issuetype = Bug ORDER BY created DESC"
            result = await self.jira_client.search(jql, max_results=50)
            data['high_priority_bugs'] = result.get('issues', [])
        
        # Project-specific stories
        projects = entities.get('projects', [])
        if projects and any(keyword in query_lower for keyword in ['story', 'stories']):
            for project in projects:
                jql = f"project = {project} AND issuetype = Story ORDER BY created DESC"
                result = await self.jira_client.search(jql, max_results=50)
                data[f'stories_{project}'] = result.get('issues', [])
        
        # Recently viewed issues
        if any(keyword in query_lower for keyword in ['viewed', 'seen', 'history']):
            jql = "issuekey in issueHistory() ORDER BY lastViewed DESC"
            result = await self.jira_client.search(jql, max_results=50)
            data['recently_viewed'] = result.get('issues', [])
        
        # jQuery/JavaScript code generation
        if any(keyword in query_lower for keyword in ['jquery', 'javascript', 'js', 'code', 'api call']):
            data['jquery_examples'] = self._generate_jquery_examples(query, entities)
        
        # If no specific pattern matched, get recent issues within last 30 days
        if not data:
            jql = "created >= -30d ORDER BY created DESC"
            result = await self.jira_client.search(jql, max_results=100)
            data['recent_issues'] = result.get('issues', [])
        
        return data
    
    async def _intelligent_assignee_search(self, assignee_name: str) -> List[Dict[str, Any]]:
        """Intelligent assignee search with fuzzy matching"""
        if not self.jira_client:
            return []
        
        # Try exact match first
        try:
            account_id = await self.jira_client.resolve_assignee_to_account_id(assignee_name)
            if account_id:
                jql = f"assignee in ({account_id}) ORDER BY updated DESC"
                result = await self.jira_client.search(jql, max_results=50)
                return result.get('issues', [])
        except Exception as e:
            print(f"Exact match failed for {assignee_name}: {e}")
        
        # Try partial name search
        try:
            jql = f'assignee ~ "{assignee_name}" ORDER BY updated DESC'
            result = await self.jira_client.search(jql, max_results=50)
            return result.get('issues', [])
        except Exception as e:
            print(f"Partial match failed for {assignee_name}: {e}")
        
        return []
    
    async def _get_assignee_suggestions(self, partial_name: str) -> List[str]:
        """Get assignee name suggestions for partial matches"""
        if not self.jira_client:
            return []
        
        try:
            # Search for users with similar names
            users = await self.jira_client._get_with_retry(
                self.jira_client._url(f"/rest/api/3/user/search?query={partial_name}")
            )
            user_data = users.json()
            suggestions = []
            for user in user_data:
                if user.get('displayName'):
                    suggestions.append(user['displayName'])
            return suggestions[:5]  # Limit to 5 suggestions
        except Exception as e:
            print(f"Failed to get suggestions for {partial_name}: {e}")
            return []
    
    async def _intelligent_story_search(self, assignee_name: str) -> List[Dict[str, Any]]:
        """Intelligent story search with name matching"""
        if not self.jira_client:
            return []
        
        # Try multiple search strategies
        strategies = [
            f'issuetype = Story AND assignee ~ "{assignee_name}" ORDER BY created DESC',
            f'issuetype = Story AND assignee was "{assignee_name}" ORDER BY created DESC',
            f'issuetype = Story AND worklogAuthor ~ "{assignee_name}" ORDER BY created DESC'
        ]
        
        all_stories = []
        for jql in strategies:
            try:
                result = await self.jira_client.search(jql, max_results=50)
                stories = result.get('issues', [])
                all_stories.extend(stories)
            except Exception as e:
                print(f"Story search failed with JQL '{jql}': {e}")
        
        # Remove duplicates based on issue key
        seen_keys = set()
        unique_stories = []
        for story in all_stories:
            if story['key'] not in seen_keys:
                seen_keys.add(story['key'])
                unique_stories.append(story)
        
        return unique_stories
    
    def _generate_jquery_examples(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate jQuery/JavaScript code examples for Jira API calls"""
        examples = {}
        
        # Basic issue search
        examples['basic_search'] = '''
// Search for issues using jQuery
$.ajax({
    url: 'https://taodigital.atlassian.net/rest/api/2/search',
    type: 'GET',
    headers: {
        'Authorization': 'Basic ' + btoa('your_email:your_api_token'),
        'Content-Type': 'application/json'
    },
    data: {
        jql: 'project = CCM ORDER BY created DESC',
        maxResults: 50
    },
    success: function(data) {
        console.log('Found issues:', data.issues);
        data.issues.forEach(function(issue) {
            console.log(issue.key + ': ' + issue.fields.summary);
        });
    },
    error: function(xhr, status, error) {
        console.error('Error:', error);
    }
});
'''
        
        # Get specific issue details
        examples['get_issue'] = '''
// Get specific issue details
function getIssueDetails(issueKey) {
    $.ajax({
        url: 'https://taodigital.atlassian.net/rest/api/2/issue/' + issueKey,
        type: 'GET',
        headers: {
            'Authorization': 'Basic ' + btoa('your_email:your_api_token'),
            'Content-Type': 'application/json'
        },
        success: function(issue) {
            console.log('Issue:', issue.key);
            console.log('Summary:', issue.fields.summary);
            console.log('Status:', issue.fields.status.name);
            console.log('Assignee:', issue.fields.assignee ? issue.fields.assignee.displayName : 'Unassigned');
        },
        error: function(xhr, status, error) {
            console.error('Error fetching issue:', error);
        }
    });
}

// Usage: getIssueDetails('CCM-283');
'''
        
        # Search by assignee
        examples['search_by_assignee'] = '''
// Search issues by assignee
function searchByAssignee(assigneeName) {
    var jql = 'assignee = "' + assigneeName + '" ORDER BY updated DESC';
    $.ajax({
        url: 'https://taodigital.atlassian.net/rest/api/2/search',
        type: 'GET',
        headers: {
            'Authorization': 'Basic ' + btoa('your_email:your_api_token'),
            'Content-Type': 'application/json'
        },
        data: {
            jql: jql,
            maxResults: 50
        },
        success: function(data) {
            console.log('Issues for', assigneeName, ':', data.issues.length);
            data.issues.forEach(function(issue) {
                console.log(issue.key + ' - ' + issue.fields.summary);
            });
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
        }
    });
}

// Usage: searchByAssignee('Ashwini');
'''
        
        # User search for fuzzy matching
        examples['user_search'] = '''
// Search for users (useful for fuzzy name matching)
function searchUsers(query) {
    $.ajax({
        url: 'https://taodigital.atlassian.net/rest/api/3/user/search',
        type: 'GET',
        headers: {
            'Authorization': 'Basic ' + btoa('your_email:your_api_token'),
            'Content-Type': 'application/json'
        },
        data: {
            query: query
        },
        success: function(users) {
            console.log('Found users:', users);
            users.forEach(function(user) {
                console.log(user.displayName + ' (' + user.emailAddress + ')');
            });
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
        }
    });
}

// Usage: searchUsers('Ashw'); // Will find users with names containing "Ashw"
'''
        
        return examples
    
    # Placeholder methods for other processing strategies
    async def _handle_predictive_analysis(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        return {'type': 'prediction', 'response': 'Predictive analysis not implemented', 'data': {}, 'confidence': 0.5}
    
    async def _handle_recommendation_engine(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        return {'type': 'recommendation', 'response': 'Recommendation engine not implemented', 'data': {}, 'confidence': 0.5}
    
    async def _handle_comparative_analysis(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        return {'type': 'comparison', 'response': 'Comparative analysis not implemented', 'data': {}, 'confidence': 0.5}
    
    async def _handle_deep_analysis(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        return {'type': 'analysis', 'response': 'Deep analysis not implemented', 'data': {}, 'confidence': 0.5}
    
    async def _handle_multi_step_analysis(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        return {'type': 'multi_step', 'response': 'Multi-step analysis not implemented', 'data': {}, 'confidence': 0.5}
    
    async def _get_sprint_data(self, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        if not self.jira_client:
            return {}
        current_sprint = await self.jira_client.get_current_sprint()
        return {'current_sprint': current_sprint}
    
    async def _get_backlog_data(self, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        if not self.jira_client:
            return {}
        backlog_items = await self.jira_client.get_backlog_items()
        return {'backlog_items': backlog_items}
    
    async def _get_project_data(self, entities: Dict[str, List[str]], query: str) -> Dict[str, Any]:
        if not self.jira_client:
            return {}
        
        data = {}
        projects = entities.get('projects', [])
        
        # Extract project keys from query if not in entities
        if not projects:
            import re
            project_matches = re.findall(r'\b(CCM|CES|GTMS|TI)\b', query, re.IGNORECASE)
            projects.extend([p.upper() for p in project_matches])
        
        for project in projects:
            project_info = await self.jira_client.get_project_info(project)
            if project_info:
                data[f'project_{project}'] = project_info
        
        return data


class EntityExtractor:
    """Extract entities from user queries"""
    
    def __init__(self):
        self.patterns = {
            'tickets': r'\b([A-Z]+-\d+)\b',
            'people': r'\b(?:ashwin|ashwini|thyagarajan|john|jane|mike|sarah|david|lisa|robert|emily|chris|amanda|karthikeyan|ramesh|ajith)\b',
            'assignees': r'\b(?:ashwin|ashwini|thyagarajan|john|jane|mike|sarah|david|lisa|robert|emily|chris|amanda|karthikeyan|ramesh|ajith)\b',
            # Enhanced patterns for partial names and variations
            'partial_names': r'\b([A-Z][a-z]+)\s+(?:stories|issues|tickets|work|assigned|worked)\b',
            'name_variations': r'\b(?:worked by|assigned to|assignee|owner|responsible)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
            'projects': r'\b(?:project|proj|initiative|program)\s+([A-Z]+)\b|(?:CCM|CES|GTMS|TI)\b',
            'sprints': r'\b(?:sprint|iteration)\s+(\d+)\b',
            'timeframes': r'\b(?:this week|last week|this month|last month|yesterday|today|current|recent|last sprint|previous sprint|last 30|past month|created recently|updated recently|resolved recently)\b',
            'statuses': r'\b(?:todo|in progress|done|completed|closed|open|blocked|resolved)\b',
            'priorities': r'\b(?:high|medium|low|critical|urgent|normal|highest|lowest)\b',
            'backlog': r'\b(?:backlog|pending|todo|not started|ready)\b',
            'sprint_terms': r'\b(?:sprint|iteration|sprint planning|sprint review|retrospective)\b',
            'issue_types': r'\b(?:story|stories|bug|bugs|task|tasks|epic|epics)\b',
            'recent_keywords': r'\b(?:recent|recently|updated|modified|changed|viewed|seen|history|created|resolved|completed|done|finished)\b'
        }
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query using patterns and AI with intelligent name matching"""
        
        entities = {}
        
        # Pattern-based extraction
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                # Flatten matches if they're tuples
                flattened = []
                for match in matches:
                    if isinstance(match, tuple):
                        flattened.extend([m for m in match if m])
                    else:
                        flattened.append(match)
                entities[entity_type] = list(set(flattened))
        
        # Enhanced assignee extraction with fuzzy matching
        if 'partial_names' in entities:
            entities['assignees'] = entities.get('assignees', []) + entities['partial_names']
        
        if 'name_variations' in entities:
            entities['assignees'] = entities.get('assignees', []) + entities['name_variations']
        
        # Clean up assignees list
        if 'assignees' in entities:
            entities['assignees'] = list(set([name.strip() for name in entities['assignees'] if name.strip()]))
        
        return entities
