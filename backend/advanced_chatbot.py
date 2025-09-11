"""
Advanced Chatbot Features
Implements semantic search, multi-intent queries, fuzzy entity recognition,
sprint health scoring, velocity forecasting, and leadership-specific insights.
"""

import re
import json
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    SPRINT_HEALTH = "sprint_health"
    TEAM_PERFORMANCE = "team_performance"
    QUALITY_METRICS = "quality_metrics"
    CROSS_PROJECT = "cross_project"
    TRENDS_ANALYSIS = "trends_analysis"
    RISK_DETECTION = "risk_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    GOAL_ALIGNMENT = "goal_alignment"
    CAPACITY_PLANNING = "capacity_planning"

@dataclass
class SprintHealthMetrics:
    """Sprint health calculation metrics"""
    committed_stories: int
    completed_stories: int
    spillover_count: int
    blocker_count: int
    bug_ratio: float
    velocity_trend: float
    health_score: float
    risk_level: str  # 'low', 'medium', 'high'

@dataclass
class VelocityForecast:
    """Velocity forecasting data"""
    current_velocity: float
    projected_velocity: float
    burn_rate: float
    days_remaining: int
    stories_remaining: int
    completion_probability: float
    confidence_level: str

@dataclass
class RiskAlert:
    """Risk detection alert"""
    type: str
    severity: str
    description: str
    ticket_keys: List[str]
    days_blocked: Optional[int]
    impact_score: float

class SemanticSearchEngine:
    """Semantic search using embeddings for fuzzy ticket matching"""
    
    def __init__(self):
        self.embeddings_cache = {}
        self.similarity_threshold = 0.7
        
    async def find_similar_tickets(self, query: str, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find tickets semantically similar to query"""
        try:
            # For now, use keyword matching with fuzzy logic
            # In production, this would use OpenAI embeddings or local embeddings
            query_lower = query.lower()
            similar_tickets = []
            
            for ticket in tickets:
                summary = ticket.get('fields', {}).get('summary', '').lower()
                description = ticket.get('fields', {}).get('description', '').lower()
                
                # Calculate similarity score based on keyword overlap
                similarity_score = self._calculate_keyword_similarity(query_lower, summary, description)
                
                if similarity_score >= self.similarity_threshold:
                    ticket['semantic_score'] = similarity_score
                    similar_tickets.append(ticket)
            
            # Sort by similarity score
            similar_tickets.sort(key=lambda x: x.get('semantic_score', 0), reverse=True)
            return similar_tickets
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    def _calculate_keyword_similarity(self, query: str, summary: str, description: str) -> float:
        """Calculate keyword-based similarity score"""
        query_words = set(query.split())
        summary_words = set(summary.split())
        description_words = set(description.split())
        
        # Calculate Jaccard similarity
        summary_overlap = len(query_words.intersection(summary_words))
        desc_overlap = len(query_words.intersection(description_words))
        
        total_words = len(query_words)
        if total_words == 0:
            return 0.0
        
        # Weight summary more than description
        similarity = (summary_overlap * 0.7 + desc_overlap * 0.3) / total_words
        return min(similarity, 1.0)

class FuzzyEntityRecognizer:
    """Fuzzy entity recognition for names and project keys"""
    
    def __init__(self):
        self.name_variations = {
            'ajith': ['ajit', 'ajith kumar', 'ajithkumar', 'ajith r', 'ajith k'],
            'priya': ['priya sharma', 'priyasharma', 'priya s'],
            'ashwin': ['ashwin thyagarajan', 'ashwin t', 'ashwinthyagarajan', 'ashwin thyag'],
            'thyagarajan': ['thyagarajan', 'thyag', 'ashwin thyagarajan'],
            'saiteja': ['sai teja', 'sai teja miriyala', 'saiteja miriyala', 'sai teja m', 'saiteja m'],
            'srikanth': ['srikanth chitturi', 'srikanth c', 'srikanthchitturi'],
            'karthikeya': ['karthikeya', 'karthik', 'karthikeya k'],
            'sai teja': ['sai teja miriyala', 'saiteja', 'sai teja m'],
            'sai teja miriyala': ['saiteja', 'sai teja', 'sai teja m']
        }
        
        self.project_variations = {
            'ccm': ['call classification', 'classification modernization'],
            'ces': ['candidate evaluation', 'evaluation system'],
            'ti': ['tao intranet', 'intranet'],
            'gtms': ['global trade', 'trade management']
        }
    
    def resolve_entity(self, entity: str, entity_type: str) -> Optional[str]:
        """Resolve fuzzy entity to canonical form"""
        entity_lower = entity.lower().strip()
        
        if entity_type == 'assignee':
            # First try exact match
            for canonical, variations in self.name_variations.items():
                if entity_lower == canonical or entity_lower in variations:
                    return self._get_full_name(canonical)
            
            # Try partial matching for names like "saiteja" -> "sai teja"
            for canonical, variations in self.name_variations.items():
                for variation in variations:
                    if self._is_partial_match(entity_lower, variation):
                        return self._get_full_name(canonical)
        
        elif entity_type == 'project':
            for canonical, variations in self.project_variations.items():
                if entity_lower in variations or entity_lower == canonical:
                    return canonical.upper()
        
        return None
    
    def _is_partial_match(self, query: str, variation: str) -> bool:
        """Check if query is a partial match of variation"""
        query_words = query.split()
        variation_words = variation.split()
        
        # Check if all query words are contained in variation
        return all(any(qw in vw for vw in variation_words) for qw in query_words)
    
    def _get_full_name(self, canonical: str) -> str:
        """Get the full display name for canonical form"""
        full_names = {
            'ajith': 'Ajith Kumar',
            'priya': 'Priya Sharma', 
            'ashwin': 'Ashwin Thyagarajan',
            'thyagarajan': 'Ashwin Thyagarajan',
            'saiteja': 'Sai Teja Miriyala',
            'sai teja': 'Sai Teja Miriyala',
            'sai teja miriyala': 'Sai Teja Miriyala',
            'srikanth': 'Srikanth Chitturi',
            'karthikeya': 'Karthikeya'
        }
        return full_names.get(canonical, canonical.title())

class MultiIntentProcessor:
    """Handle multi-intent queries like 'Show Ajith's bugs and Priya's stories'"""
    
    def __init__(self, fuzzy_recognizer: FuzzyEntityRecognizer):
        self.fuzzy_recognizer = fuzzy_recognizer
    
    def parse_multi_intent_query(self, query: str) -> List[Dict[str, Any]]:
        """Parse complex queries into multiple intents"""
        intents = []
        
        # Pattern: "Show [person1]'s [type1] and [person2]'s [type2]"
        pattern = r"show\s+([^']+)'s\s+(\w+)\s+and\s+([^']+)'s\s+(\w+)"
        match = re.search(pattern, query.lower())
        
        if match:
            person1, type1, person2, type2 = match.groups()
            
            # Resolve fuzzy names
            resolved_person1 = self.fuzzy_recognizer.resolve_entity(person1, 'assignee')
            resolved_person2 = self.fuzzy_recognizer.resolve_entity(person2, 'assignee')
            
            if resolved_person1 and resolved_person2:
                intents.extend([
                    {
                        'type': 'assignee_issue_type',
                        'assignee': resolved_person1,
                        'issue_type': type1.title(),
                        'description': f"{resolved_person1}'s {type1}"
                    },
                    {
                        'type': 'assignee_issue_type',
                        'assignee': resolved_person2,
                        'issue_type': type2.title(),
                        'description': f"{resolved_person2}'s {type2}"
                    }
                ])
        
        # Pattern: "Compare [person1] vs [person2]"
        compare_pattern = r"compare\s+([^vs]+)\s+vs?\s+([^\s]+)"
        compare_match = re.search(compare_pattern, query.lower())
        
        if compare_match:
            person1, person2 = compare_match.groups()
            resolved_person1 = self.fuzzy_recognizer.resolve_entity(person1.strip(), 'assignee')
            resolved_person2 = self.fuzzy_recognizer.resolve_entity(person2.strip(), 'assignee')
            
            if resolved_person1 and resolved_person2:
                intents.append({
                    'type': 'comparison',
                    'entities': [resolved_person1, resolved_person2],
                    'description': f"Compare {resolved_person1} vs {resolved_person2}"
                })
        
        return intents

class SprintHealthCalculator:
    """Calculate sprint health scores and metrics"""
    
    def calculate_health_score(self, sprint_data: Dict[str, Any]) -> SprintHealthMetrics:
        """Calculate comprehensive sprint health score"""
        
        issues = sprint_data.get('issues', [])
        total_issues = len(issues)
        
        if total_issues == 0:
            return SprintHealthMetrics(
                committed_stories=0, completed_stories=0, spillover_count=0,
                blocker_count=0, bug_ratio=0.0, velocity_trend=0.0,
                health_score=0.0, risk_level='low'
            )
        
        # Count by status and type
        stories = [i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Story']
        bugs = [i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Bug']
        
        completed_stories = len([s for s in stories if s.get('fields', {}).get('status', {}).get('name') in ['Done', 'Closed']])
        committed_stories = len(stories)
        
        blocked_issues = len([i for i in issues if i.get('fields', {}).get('status', {}).get('name') in ['Blocked', 'Waiting']])
        
        # Calculate metrics
        bug_ratio = len(bugs) / total_issues if total_issues > 0 else 0.0
        completion_rate = completed_stories / committed_stories if committed_stories > 0 else 0.0
        
        # Calculate health score
        base_score = completion_rate
        
        # Penalties
        spillover_penalty = min(0.2, blocked_issues * 0.05)  # Max 20% penalty
        blocker_penalty = min(0.3, blocked_issues * 0.1)      # Max 30% penalty
        bug_penalty = min(0.2, bug_ratio * 0.5)               # Max 20% penalty for high bug ratio
        
        health_score = max(0.0, base_score - spillover_penalty - blocker_penalty - bug_penalty)
        
        # Determine risk level
        if health_score >= 0.8:
            risk_level = 'low'
        elif health_score >= 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return SprintHealthMetrics(
            committed_stories=committed_stories,
            completed_stories=completed_stories,
            spillover_count=blocked_issues,
            blocker_count=blocked_issues,
            bug_ratio=bug_ratio,
            velocity_trend=completion_rate,
            health_score=health_score,
            risk_level=risk_level
        )

class VelocityForecaster:
    """Predict sprint completion based on burn rate"""
    
    def forecast_velocity(self, sprint_data: Dict[str, Any], days_remaining: int) -> VelocityForecast:
        """Forecast sprint completion probability"""
        
        issues = sprint_data.get('issues', [])
        if not issues:
            return VelocityForecast(
                current_velocity=0.0, projected_velocity=0.0, burn_rate=0.0,
                days_remaining=days_remaining, stories_remaining=0,
                completion_probability=0.0, confidence_level='low'
            )
        
        # Calculate current velocity (stories completed)
        completed_stories = len([
            i for i in issues 
            if i.get('fields', {}).get('issuetype', {}).get('name') == 'Story' and
            i.get('fields', {}).get('status', {}).get('name') in ['Done', 'Closed']
        ])
        
        total_stories = len([i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Story'])
        remaining_stories = total_stories - completed_stories
        
        # Calculate burn rate (stories per day)
        sprint_duration = 14  # Assume 2-week sprint
        days_elapsed = sprint_duration - days_remaining
        burn_rate = completed_stories / max(days_elapsed, 1)
        
        # Project completion
        projected_velocity = burn_rate * days_remaining
        completion_probability = min(1.0, projected_velocity / max(remaining_stories, 1))
        
        # Determine confidence
        if days_elapsed >= 7:  # At least a week of data
            confidence_level = 'high'
        elif days_elapsed >= 3:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'
        
        return VelocityForecast(
            current_velocity=completed_stories,
            projected_velocity=projected_velocity,
            burn_rate=burn_rate,
            days_remaining=days_remaining,
            stories_remaining=remaining_stories,
            completion_probability=completion_probability,
            confidence_level=confidence_level
        )

class AdvancedRiskDetector:
    """Advanced risk detection with multiple risk types"""
    
    def detect_risks(self, sprint_data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect various types of risks"""
        risks = []
        issues = sprint_data.get('issues', [])
        
        # Risk 1: Long-blocked tickets
        for issue in issues:
            if issue.get('fields', {}).get('status', {}).get('name') in ['Blocked', 'Waiting']:
                created_date = issue.get('fields', {}).get('created', '')
                if created_date:
                    try:
                        created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        days_blocked = (datetime.now(timezone.utc) - created_dt).days
                        
                        if days_blocked > 5:
                            risks.append(RiskAlert(
                                type='long_blocked',
                                severity='high' if days_blocked > 10 else 'medium',
                                description=f"Ticket blocked for {days_blocked} days",
                                ticket_keys=[issue.get('key')],
                                days_blocked=days_blocked,
                                impact_score=min(1.0, days_blocked / 20)
                            ))
                    except Exception:
                        continue
        
        # Risk 2: High bug ratio
        bugs = [i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Bug']
        bug_ratio = len(bugs) / len(issues) if issues else 0
        
        if bug_ratio > 0.3:  # More than 30% bugs
            risks.append(RiskAlert(
                type='high_bug_ratio',
                severity='medium',
                description=f"High bug ratio: {bug_ratio:.1%}",
                ticket_keys=[b.get('key') for b in bugs[:5]],  # Top 5 bugs
                days_blocked=None,
                impact_score=bug_ratio
            ))
        
        # Risk 3: Too many spillovers
        spillover_count = len([i for i in issues if i.get('fields', {}).get('status', {}).get('name') in ['Blocked', 'Waiting']])
        if spillover_count > len(issues) * 0.2:  # More than 20% blocked
            risks.append(RiskAlert(
                type='high_spillover',
                severity='high',
                description=f"High spillover rate: {spillover_count} tickets blocked",
                ticket_keys=[i.get('key') for i in issues if i.get('fields', {}).get('status', {}).get('name') in ['Blocked', 'Waiting']],
                days_blocked=None,
                impact_score=min(1.0, spillover_count / len(issues))
            ))
        
        return risks

class AnomalyDetector:
    """Detect anomalies in sprint data"""
    
    def detect_anomalies(self, historical_data: List[Dict[str, Any]], current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies by comparing current data to historical patterns"""
        anomalies = []
        
        if not historical_data:
            return anomalies
        
        # Calculate historical averages
        historical_bug_counts = []
        historical_reopen_counts = []
        
        for sprint in historical_data:
            issues = sprint.get('issues', [])
            bug_count = len([i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Bug'])
            historical_bug_counts.append(bug_count)
            
            # Count reopened issues (simplified - in reality would check changelog)
            reopen_count = len([i for i in issues if 'reopen' in i.get('fields', {}).get('status', {}).get('name', '').lower()])
            historical_reopen_counts.append(reopen_count)
        
        # Current data
        current_issues = current_data.get('issues', [])
        current_bug_count = len([i for i in current_issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Bug'])
        
        # Detect bug spike
        if historical_bug_counts:
            avg_bugs = np.mean(historical_bug_counts)
            std_bugs = np.std(historical_bug_counts)
            
            if current_bug_count > avg_bugs + 2 * std_bugs:  # 2 standard deviations above mean
                anomalies.append({
                    'type': 'bug_spike',
                    'severity': 'high',
                    'description': f"Bug count spike: {current_bug_count} vs historical average {avg_bugs:.1f}",
                    'current_value': current_bug_count,
                    'historical_average': avg_bugs,
                    'deviation': (current_bug_count - avg_bugs) / std_bugs if std_bugs > 0 else 0
                })
        
        return anomalies

class AdvancedChatbotEngine:
    """Main advanced chatbot engine integrating all features"""
    
    def __init__(self, jira_client):
        self.jira_client = jira_client
        self.semantic_search = SemanticSearchEngine()
        self.fuzzy_recognizer = FuzzyEntityRecognizer()
        self.multi_intent_processor = MultiIntentProcessor(self.fuzzy_recognizer)
        self.health_calculator = SprintHealthCalculator()
        self.velocity_forecaster = VelocityForecaster()
        self.risk_detector = AdvancedRiskDetector()
        self.anomaly_detector = AnomalyDetector()
        
    async def process_advanced_query(self, query: str) -> Dict[str, Any]:
        """Process query with advanced features"""
        
        # 1. Parse multi-intent queries
        intents = self.multi_intent_processor.parse_multi_intent_query(query)
        
        # 2. Determine query type
        query_type = self._classify_query(query)
        
        # 3. Execute appropriate processing
        if query_type == QueryIntent.SPRINT_HEALTH:
            return await self._process_sprint_health_query(query)
        elif query_type == QueryIntent.TEAM_PERFORMANCE:
            return await self._process_team_performance_query(query, intents)
        elif query_type == QueryIntent.QUALITY_METRICS:
            return await self._process_quality_metrics_query(query)
        elif query_type == QueryIntent.CROSS_PROJECT:
            return await self._process_cross_project_query(query)
        elif query_type == QueryIntent.TRENDS_ANALYSIS:
            return await self._process_trends_query(query)
        else:
            return await self._process_general_query(query, intents)
    
    def _classify_query(self, query: str) -> QueryIntent:
        """Classify query intent"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['sprint health', 'sprint status', 'burndown', 'velocity']):
            return QueryIntent.SPRINT_HEALTH
        elif any(word in query_lower for word in ['compare', 'team', 'workload', 'performance']):
            return QueryIntent.TEAM_PERFORMANCE
        elif any(word in query_lower for word in ['bug', 'quality', 'defect', 'reopen']):
            return QueryIntent.QUALITY_METRICS
        elif any(word in query_lower for word in ['project', 'ccm', 'ces', 'ti', 'gtms']):
            return QueryIntent.CROSS_PROJECT
        elif any(word in query_lower for word in ['trend', 'last', 'history', 'over time']):
            return QueryIntent.TRENDS_ANALYSIS
        else:
            return QueryIntent.SPRINT_HEALTH  # Default
    
    async def _process_sprint_health_query(self, query: str) -> Dict[str, Any]:
        """Process sprint health queries"""
        try:
            # Get current sprint data
            sprint_data = await self._get_current_sprint_data()
            
            # Calculate health metrics
            health_metrics = self.health_calculator.calculate_health_score(sprint_data)
            
            # Forecast velocity
            days_remaining = 7  # Assume 7 days remaining
            velocity_forecast = self.velocity_forecaster.forecast_velocity(sprint_data, days_remaining)
            
            # Detect risks
            risks = self.risk_detector.detect_risks(sprint_data)
            
            # Generate response
            response = self._format_sprint_health_response(health_metrics, velocity_forecast, risks)
            
            return {
                'response': response,
                'metrics': {
                    'health_score': health_metrics.health_score,
                    'risk_level': health_metrics.risk_level,
                    'completion_probability': velocity_forecast.completion_probability
                },
                'risks': [{'type': r.type, 'severity': r.severity, 'description': r.description} for r in risks]
            }
            
        except Exception as e:
            logger.error(f"Sprint health query error: {e}")
            return {'response': f"Error processing sprint health query: {str(e)}", 'error': True}
    
    async def _process_team_performance_query(self, query: str, intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process team performance queries"""
        try:
            if not intents:
                return {'response': "Could not parse team performance query", 'error': True}
            
            results = []
            for intent in intents:
                if intent['type'] == 'comparison':
                    comparison_result = await self._generate_comparison_data(intent['entities'])
                    results.append(comparison_result)
                elif intent['type'] == 'assignee_issue_type':
                    assignee_result = await self._generate_assignee_data(intent['assignee'], intent['issue_type'])
                    results.append(assignee_result)
            
            response = self._format_team_performance_response(results)
            
            return {
                'response': response,
                'comparison_data': results
            }
            
        except Exception as e:
            logger.error(f"Team performance query error: {e}")
            return {'response': f"Error processing team performance query: {str(e)}", 'error': True}
    
    async def _get_current_sprint_data(self) -> Dict[str, Any]:
        """Get current sprint data"""
        try:
            # Get current sprint
            sprints = await self.jira_client.get_active_sprints()
            if not sprints:
                return {'issues': []}
            
            current_sprint = sprints[0]
            sprint_id = current_sprint.get('id')
            
            # Get sprint issues - use same JQL as Jira UI
            jql = "sprint in openSprints() AND issuetype = Story ORDER BY created DESC"
            sprint_data = await self.jira_client.search(jql, max_results=1000)
            
            return sprint_data
            
        except Exception as e:
            logger.error(f"Error getting sprint data: {e}")
            return {'issues': []}
    
    async def _generate_comparison_data(self, entities: List[str]) -> Dict[str, Any]:
        """Generate comparison data for entities"""
        comparison_data = {}
        
        for entity in entities:
            # Get entity info
            assignee_info = self.jira_client.get_assignee_info(entity)
            if assignee_info:
                # Get tickets for this assignee
                jql = f'assignee = "{assignee_info["accountId"]}"'
                tickets = await self.jira_client.search(jql, max_results=100)
                
                # Calculate metrics
                issues = tickets.get('issues', [])
                completed = len([i for i in issues if i.get('fields', {}).get('status', {}).get('name') in ['Done', 'Closed']])
                in_progress = len([i for i in issues if i.get('fields', {}).get('status', {}).get('name') == 'In Progress'])
                
                comparison_data[entity] = {
                    'total_tickets': len(issues),
                    'completed': completed,
                    'in_progress': in_progress,
                    'completion_rate': completed / len(issues) if issues else 0
                }
        
        return comparison_data
    
    async def _generate_assignee_data(self, assignee: str, issue_type: str) -> Dict[str, Any]:
        """Generate data for specific assignee and issue type"""
        assignee_info = self.jira_client.get_assignee_info(assignee)
        if not assignee_info:
            return {}
        
        jql = f'assignee = "{assignee_info["accountId"]}" AND issuetype = "{issue_type}"'
        tickets = await self.jira_client.search(jql, max_results=100)
        
        return {
            'assignee': assignee,
            'issue_type': issue_type,
            'tickets': tickets.get('issues', [])
        }
    
    def _format_sprint_health_response(self, health_metrics: SprintHealthMetrics, 
                                     velocity_forecast: VelocityForecast, 
                                     risks: List[RiskAlert]) -> str:
        """Format sprint health response with rich Markdown"""
        
        # Health score with emoji
        health_emoji = "🟢" if health_metrics.health_score >= 0.8 else "🟡" if health_metrics.health_score >= 0.6 else "🔴"
        
        response = f"""## Sprint Health Dashboard {health_emoji}

### 📊 **Health Score: {health_metrics.health_score:.1%}**
- **Risk Level:** {health_metrics.risk_level.upper()}
- **Committed Stories:** {health_metrics.committed_stories}
- **Completed Stories:** {health_metrics.completed_stories}
- **Completion Rate:** {health_metrics.velocity_trend:.1%}

### 🚀 **Velocity Forecast**
- **Current Velocity:** {velocity_forecast.current_velocity:.1f} stories
- **Projected Completion:** {velocity_forecast.completion_probability:.1%}
- **Burn Rate:** {velocity_forecast.burn_rate:.1f} stories/day
- **Days Remaining:** {velocity_forecast.days_remaining}
- **Confidence:** {velocity_forecast.confidence_level.title()}

### ⚠️ **Risk Alerts**"""
        
        if risks:
            for risk in risks:
                severity_emoji = "🔴" if risk.severity == 'high' else "🟡" if risk.severity == 'medium' else "🟢"
                response += f"\n- {severity_emoji} **{risk.type.replace('_', ' ').title()}:** {risk.description}"
        else:
            response += "\n- ✅ No significant risks detected"
        
        return response
    
    def _format_team_performance_response(self, results: List[Dict[str, Any]]) -> str:
        """Format team performance response"""
        
        response = "## Team Performance Analysis\n\n"
        
        for result in results:
            if 'comparison_data' in result:
                response += "### 👥 **Team Comparison**\n\n"
                response += "| Team Member | Total Tickets | Completed | In Progress | Completion Rate |\n"
                response += "|-------------|---------------|-----------|-------------|----------------|\n"
                
                for member, data in result['comparison_data'].items():
                    response += f"| {member} | {data['total_tickets']} | {data['completed']} | {data['in_progress']} | {data['completion_rate']:.1%} |\n"
                
                response += "\n"
        
        return response
    
    async def _process_quality_metrics_query(self, query: str) -> Dict[str, Any]:
        """Process quality metrics queries"""
        # Implementation for quality metrics
        return {'response': 'Quality metrics analysis coming soon...'}
    
    async def _process_cross_project_query(self, query: str) -> Dict[str, Any]:
        """Process cross-project queries"""
        # Implementation for cross-project analysis
        return {'response': 'Cross-project analysis coming soon...'}
    
    async def _process_trends_query(self, query: str) -> Dict[str, Any]:
        """Process trends analysis queries"""
        # Implementation for trends analysis
        return {'response': 'Trends analysis coming soon...'}
    
    async def _process_general_query(self, query: str, intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process general queries with semantic search"""
        try:
            # Get current sprint data for semantic search
            sprint_data = await self._get_current_sprint_data()
            
            # Use semantic search to find relevant tickets
            similar_tickets = await self.semantic_search.find_similar_tickets(query, sprint_data.get('issues', []))
            
            if similar_tickets:
                response = f"## Semantic Search Results\n\nFound {len(similar_tickets)} relevant tickets:\n\n"
                
                for ticket in similar_tickets[:5]:  # Show top 5
                    key = ticket.get('key')
                    summary = ticket.get('fields', {}).get('summary', '')
                    status = ticket.get('fields', {}).get('status', {}).get('name', '')
                    url = f"{self.jira_client.cfg.base_url}/browse/{key}"
                    
                    response += f"- **[{key}]({url})**: {summary} ({status})\n"
                
                return {
                    'response': response,
                    'semantic_results': similar_tickets[:5]
                }
            else:
                return {'response': "No relevant tickets found for your query."}
                
        except Exception as e:
            logger.error(f"General query error: {e}")
            return {'response': f"Error processing query: {str(e)}", 'error': True}
