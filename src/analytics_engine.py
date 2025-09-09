"""
Advanced Analytics Engine with Predictive Capabilities
Provides intelligent analytics, forecasting, and anomaly detection
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from ai_engine import AIInsight, AdvancedAIEngine
from jira_client import JiraClient

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric: str
    trend_direction: str  # 'increasing', 'decreasing', 'stable', 'volatile'
    trend_strength: float  # 0-1
    confidence: float  # 0-1
    data_points: List[float]
    prediction: Optional[float] = None
    timeframe: str = 'weekly'

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    metric: str
    anomaly_type: str  # 'spike', 'drop', 'pattern_change', 'outlier'
    severity: str  # 'low', 'medium', 'high', 'critical'
    confidence: float  # 0-1
    affected_entities: List[str]
    description: str
    recommended_action: str

class AdvancedAnalyticsEngine:
    """Advanced analytics engine with AI-powered insights"""
    
    def __init__(self, ai_engine: AdvancedAIEngine, jira_client: Optional[JiraClient] = None):
        self.ai_engine = ai_engine
        self.jira_client = jira_client
        self.historical_data = {}
        self.metrics_cache = {}
        
    async def generate_comprehensive_analytics(self, query: str = None) -> Dict[str, Any]:
        """Generate comprehensive analytics with AI insights"""
        
        # Get raw data
        raw_data = await self._collect_comprehensive_data()
        
        # Process analytics
        analytics = await self._process_analytics(raw_data)
        
        # Generate AI insights
        ai_insights = await self._generate_ai_insights(analytics, query)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(analytics)
        
        # Generate predictions
        predictions = await self._generate_predictions(analytics)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(analytics, anomalies, predictions)
        
        return {
            'summary': analytics['summary'],
            'projects': analytics['projects'],
            'trends': analytics['trends'],
            'ai_insights': ai_insights,
            'anomalies': [anomaly.__dict__ for anomaly in anomalies],
            'predictions': predictions,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat(),
            'data_freshness': self._calculate_data_freshness(raw_data)
        }
    
    async def _collect_comprehensive_data(self) -> Dict[str, Any]:
        """Collect comprehensive data from Jira"""
        
        if not self.jira_client:
            return {}
        
        # Get all issues
        # Use time-bounded JQL to avoid expensive broad scans
        all_issues_jql = "updated >= -30d ORDER BY updated DESC"
        all_issues = self.jira_client.search(all_issues_jql, max_results=2000)
        
        # Get current sprint
        current_sprint = self.jira_client.get_current_sprint()
        
        # Get historical data (last 90 days)
        historical_jql = "updated >= -90d ORDER BY updated DESC"
        historical_issues = self.jira_client.search(historical_jql, max_results=1000)
        
        return {
            'all_issues': all_issues.get('issues', []),
            'historical_issues': historical_issues.get('issues', []),
            'current_sprint': current_sprint,
            'total_count': all_issues.get('total', 0)
        }
    
    async def _process_analytics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw data into analytics"""
        
        issues = raw_data.get('all_issues', [])
        historical_issues = raw_data.get('historical_issues', [])
        
        # Process projects
        projects = self._analyze_projects(issues)
        
        # Process trends
        trends = self._analyze_trends(historical_issues)
        
        # Calculate summary metrics
        summary = self._calculate_summary_metrics(issues, projects)
        
        return {
            'summary': summary,
            'projects': projects,
            'trends': trends,
            'raw_data': raw_data
        }
    
    def _analyze_projects(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze project-level metrics"""
        
        projects = {}
        
        for issue in issues:
            fields = issue.get('fields', {})
            project_key = fields.get('project', {}).get('key', 'Unknown')
            project_name = fields.get('project', {}).get('name', 'Unknown')
            
            if project_key not in projects:
                projects[project_key] = {
                    'name': project_name,
                    'stories': 0,
                    'defects': 0,
                    'tasks': 0,
                    'total_issues': 0,
                    'assignees': set(),
                    'status_counts': {},
                    'priority_counts': {},
                    'created_dates': [],
                    'updated_dates': [],
                    'resolution_times': []
                }
            
            project_data = projects[project_key]
            project_data['total_issues'] += 1
            
            # Count by issue type
            issue_type = fields.get('issuetype', {}).get('name', '').lower()
            if 'story' in issue_type:
                project_data['stories'] += 1
            elif 'bug' in issue_type or 'defect' in issue_type:
                project_data['defects'] += 1
            elif 'task' in issue_type:
                project_data['tasks'] += 1
            
            # Count assignees
            assignee = fields.get('assignee')
            if assignee and assignee.get('displayName'):
                project_data['assignees'].add(assignee.get('displayName'))
            
            # Count statuses
            status = fields.get('status', {}).get('name', 'Unknown')
            project_data['status_counts'][status] = project_data['status_counts'].get(status, 0) + 1
            
            # Count priorities
            priority = fields.get('priority', {}).get('name', 'Unknown')
            project_data['priority_counts'][priority] = project_data['priority_counts'].get(priority, 0) + 1
            
            # Track dates
            created = fields.get('created')
            updated = fields.get('updated')
            if created:
                project_data['created_dates'].append(created)
            if updated:
                project_data['updated_dates'].append(updated)
        
        # Convert sets to counts and calculate additional metrics
        for project_key, project_data in projects.items():
            project_data['assignee_count'] = len(project_data['assignees'])
            project_data['assignees'] = list(project_data['assignees'])
            
            # Calculate defect ratio
            stories = project_data['stories']
            defects = project_data['defects']
            project_data['defect_ratio'] = (defects / stories * 100) if stories > 0 else 0
            
            # Calculate health score
            project_data['health_score'] = self._calculate_project_health_score(project_data)
        
        return projects
    
    def _analyze_trends(self, historical_issues: List[Dict[str, Any]]) -> Dict[str, TrendAnalysis]:
        """Analyze trends in historical data"""
        
        trends = {}
        
        # Group issues by week
        weekly_data = self._group_issues_by_week(historical_issues)
        
        # Analyze velocity trend
        velocity_trend = self._analyze_velocity_trend(weekly_data)
        if velocity_trend:
            trends['velocity'] = velocity_trend
        
        # Analyze defect trend
        defect_trend = self._analyze_defect_trend(weekly_data)
        if defect_trend:
            trends['defects'] = defect_trend
        
        # Analyze completion trend
        completion_trend = self._analyze_completion_trend(weekly_data)
        if completion_trend:
            trends['completion'] = completion_trend
        
        return trends
    
    def _group_issues_by_week(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group issues by week for trend analysis"""
        
        weekly_data = {}
        
        for issue in issues:
            fields = issue.get('fields', {})
            updated = fields.get('updated')
            
            if updated:
                # Parse date and get week
                try:
                    date_obj = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    week_key = date_obj.strftime('%Y-W%U')
                    
                    if week_key not in weekly_data:
                        weekly_data[week_key] = []
                    
                    weekly_data[week_key].append(issue)
                except Exception:
                    continue
        
        return weekly_data
    
    def _analyze_velocity_trend(self, weekly_data: Dict[str, List[Dict[str, Any]]]) -> Optional[TrendAnalysis]:
        """Analyze velocity trend"""
        
        weekly_velocity = []
        
        for week, issues in weekly_data.items():
            completed_stories = 0
            for issue in issues:
                fields = issue.get('fields', {})
                status = fields.get('status', {}).get('name', '').lower()
                issue_type = fields.get('issuetype', {}).get('name', '').lower()
                
                if 'done' in status or 'completed' in status or 'closed' in status:
                    if 'story' in issue_type:
                        completed_stories += 1
            
            weekly_velocity.append(completed_stories)
        
        if len(weekly_velocity) < 3:
            return None
        
        return self._calculate_trend('velocity', weekly_velocity)
    
    def _analyze_defect_trend(self, weekly_data: Dict[str, List[Dict[str, Any]]]) -> Optional[TrendAnalysis]:
        """Analyze defect trend"""
        
        weekly_defects = []
        
        for week, issues in weekly_data.items():
            defects = 0
            for issue in issues:
                fields = issue.get('fields', {})
                issue_type = fields.get('issuetype', {}).get('name', '').lower()
                
                if 'bug' in issue_type or 'defect' in issue_type:
                    defects += 1
            
            weekly_defects.append(defects)
        
        if len(weekly_defects) < 3:
            return None
        
        return self._calculate_trend('defects', weekly_defects)
    
    def _analyze_completion_trend(self, weekly_data: Dict[str, List[Dict[str, Any]]]) -> Optional[TrendAnalysis]:
        """Analyze completion trend"""
        
        weekly_completions = []
        
        for week, issues in weekly_data.items():
            completions = 0
            for issue in issues:
                fields = issue.get('fields', {})
                status = fields.get('status', {}).get('name', '').lower()
                
                if 'done' in status or 'completed' in status or 'closed' in status:
                    completions += 1
            
            weekly_completions.append(completions)
        
        if len(weekly_completions) < 3:
            return None
        
        return self._calculate_trend('completion', weekly_completions)
    
    def _calculate_trend(self, metric: str, data_points: List[float]) -> TrendAnalysis:
        """Calculate trend from data points"""
        
        if len(data_points) < 2:
            return None
        
        # Calculate trend direction and strength
        x = np.arange(len(data_points))
        y = np.array(data_points)
        
        # Linear regression
        slope = np.polyfit(x, y, 1)[0]
        
        # Determine trend direction
        if abs(slope) < 0.1:
            trend_direction = 'stable'
        elif slope > 0:
            trend_direction = 'increasing'
        else:
            trend_direction = 'decreasing'
        
        # Calculate trend strength (R-squared)
        correlation_matrix = np.corrcoef(x, y)
        correlation_xy = correlation_matrix[0, 1]
        trend_strength = correlation_xy ** 2
        
        # Calculate confidence based on data points and correlation
        confidence = min(0.9, max(0.3, trend_strength * (len(data_points) / 10)))
        
        # Simple prediction (extend trend)
        prediction = None
        if len(data_points) >= 3:
            prediction = data_points[-1] + slope
        
        return TrendAnalysis(
            metric=metric,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            confidence=confidence,
            data_points=data_points,
            prediction=prediction
        )
    
    def _calculate_project_health_score(self, project_data: Dict[str, Any]) -> float:
        """Calculate project health score (0-100)"""
        
        score = 100.0
        
        # Penalize high defect ratio
        defect_ratio = project_data.get('defect_ratio', 0)
        if defect_ratio > 20:
            score -= min(30, defect_ratio - 20)
        
        # Penalize low completion rate
        status_counts = project_data.get('status_counts', {})
        total_issues = project_data.get('total_issues', 0)
        
        if total_issues > 0:
            completed = sum(count for status, count in status_counts.items() 
                          if 'done' in status.lower() or 'completed' in status.lower())
            completion_rate = (completed / total_issues) * 100
            
            if completion_rate < 50:
                score -= (50 - completion_rate) * 0.5
        
        # Reward good assignee distribution
        assignee_count = project_data.get('assignee_count', 0)
        if assignee_count > 0:
            avg_issues_per_assignee = total_issues / assignee_count
            if avg_issues_per_assignee > 20:  # Overloaded
                score -= 10
            elif avg_issues_per_assignee < 5:  # Underutilized
                score -= 5
        
        return max(0, min(100, score))
    
    def _calculate_summary_metrics(self, issues: List[Dict[str, Any]], projects: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary metrics"""
        
        total_issues = len(issues)
        total_projects = len(projects)
        
        # Count by type
        stories = sum(p['stories'] for p in projects.values())
        defects = sum(p['defects'] for p in projects.values())
        tasks = sum(p['tasks'] for p in projects.values())
        
        # Count assignees
        all_assignees = set()
        for project in projects.values():
            all_assignees.update(project.get('assignees', []))
        
        # Calculate health metrics
        avg_health_score = np.mean([p['health_score'] for p in projects.values()]) if projects else 0
        healthy_projects = sum(1 for p in projects.values() if p['health_score'] > 70)
        
        return {
            'total_issues': total_issues,
            'total_projects': total_projects,
            'total_stories': stories,
            'total_defects': defects,
            'total_tasks': tasks,
            'total_assignees': len(all_assignees),
            'avg_health_score': avg_health_score,
            'healthy_projects': healthy_projects,
            'defect_ratio': (defects / stories * 100) if stories > 0 else 0
        }
    
    async def _generate_ai_insights(self, analytics: Dict[str, Any], query: str = None) -> List[str]:
        """Generate AI-powered insights"""
        
        insights_prompt = f"""
        Analyze this comprehensive Jira analytics data and provide 5-7 key insights:
        
        Analytics Data: {json.dumps(analytics, indent=2)[:3000]}
        
        Focus on:
        1. Performance patterns and trends
        2. Team productivity indicators
        3. Quality metrics and issues
        4. Project health and risks
        5. Resource utilization
        6. Process efficiency
        7. Opportunities for improvement
        
        Provide specific, actionable insights with metrics and context.
        """
        
        try:
            from llm import chat
            insights = chat([{"role": "user", "content": insights_prompt}])
            return insights.split('\n') if insights else []
        except Exception as e:
            return [f"Unable to generate insights: {str(e)}"]
    
    async def _detect_anomalies(self, analytics: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect anomalies in the data"""
        
        anomalies = []
        
        # Check for high defect ratios
        projects = analytics.get('projects', {})
        for project_key, project_data in projects.items():
            defect_ratio = project_data.get('defect_ratio', 0)
            
            if defect_ratio > 30:  # Critical threshold
                anomalies.append(AnomalyDetection(
                    metric='defect_ratio',
                    anomaly_type='spike',
                    severity='critical',
                    confidence=0.9,
                    affected_entities=[project_key],
                    description=f'Critical defect ratio of {defect_ratio:.1f}% in {project_key}',
                    recommended_action='Immediate quality review and process improvement'
                ))
            elif defect_ratio > 20:  # High threshold
                anomalies.append(AnomalyDetection(
                    metric='defect_ratio',
                    anomaly_type='spike',
                    severity='high',
                    confidence=0.8,
                    affected_entities=[project_key],
                    description=f'High defect ratio of {defect_ratio:.1f}% in {project_key}',
                    recommended_action='Quality process review and testing improvement'
                ))
        
        # Check for low health scores
        for project_key, project_data in projects.items():
            health_score = project_data.get('health_score', 0)
            
            if health_score < 30:  # Critical threshold
                anomalies.append(AnomalyDetection(
                    metric='health_score',
                    anomaly_type='drop',
                    severity='critical',
                    confidence=0.9,
                    affected_entities=[project_key],
                    description=f'Critical health score of {health_score:.1f} in {project_key}',
                    recommended_action='Immediate project review and intervention'
                ))
        
        # Check for workload anomalies
        summary = analytics.get('summary', {})
        total_issues = summary.get('total_issues', 0)
        total_assignees = summary.get('total_assignees', 0)
        
        if total_assignees > 0:
            avg_workload = total_issues / total_assignees
            
            if avg_workload > 25:  # Critical overload
                anomalies.append(AnomalyDetection(
                    metric='workload',
                    anomaly_type='spike',
                    severity='critical',
                    confidence=0.9,
                    affected_entities=['team'],
                    description=f'Critical team overload: {avg_workload:.1f} issues per person',
                    recommended_action='Immediate resource allocation and workload redistribution'
                ))
        
        return anomalies
    
    async def _generate_predictions(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions based on trends"""
        
        predictions = {}
        trends = analytics.get('trends', {})
        
        for metric, trend in trends.items():
            if trend.prediction is not None:
                predictions[metric] = {
                    'current_value': trend.data_points[-1] if trend.data_points else 0,
                    'predicted_value': trend.prediction,
                    'confidence': trend.confidence,
                    'trend_direction': trend.trend_direction,
                    'timeframe': 'next_week'
                }
        
        return predictions
    
    async def _generate_recommendations(self, analytics: Dict[str, Any], anomalies: List[AnomalyDetection], predictions: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Recommendations based on anomalies
        for anomaly in anomalies:
            if anomaly.severity in ['critical', 'high']:
                recommendations.append(anomaly.recommended_action)
        
        # Recommendations based on trends
        trends = analytics.get('trends', {})
        for metric, trend in trends.items():
            if trend.trend_direction == 'decreasing' and trend.confidence > 0.7:
                if metric == 'velocity':
                    recommendations.append("Consider sprint planning review - velocity is declining")
                elif metric == 'completion':
                    recommendations.append("Review completion processes - completion rate is declining")
        
        # General recommendations based on summary
        summary = analytics.get('summary', {})
        
        if summary.get('defect_ratio', 0) > 15:
            recommendations.append("Implement additional testing processes to reduce defect ratio")
        
        if summary.get('avg_health_score', 0) < 70:
            recommendations.append("Focus on project health improvement initiatives")
        
        if summary.get('healthy_projects', 0) < len(analytics.get('projects', {})) * 0.7:
            recommendations.append("Review and improve processes across multiple projects")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _calculate_data_freshness(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data freshness metrics"""
        
        issues = raw_data.get('all_issues', [])
        
        if not issues:
            return {'status': 'no_data', 'last_update': None}
        
        # Find most recent update
        latest_update = None
        for issue in issues:
            fields = issue.get('fields', {})
            updated = fields.get('updated')
            
            if updated:
                try:
                    date_obj = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    if latest_update is None or date_obj > latest_update:
                        latest_update = date_obj
                except Exception:
                    continue
        
        if latest_update:
            time_diff = datetime.now(latest_update.tzinfo) - latest_update
            hours_ago = time_diff.total_seconds() / 3600
            
            if hours_ago < 1:
                freshness_status = 'very_fresh'
            elif hours_ago < 24:
                freshness_status = 'fresh'
            elif hours_ago < 72:
                freshness_status = 'stale'
            else:
                freshness_status = 'very_stale'
            
            return {
                'status': freshness_status,
                'last_update': latest_update.isoformat(),
                'hours_ago': hours_ago
            }
        
        return {'status': 'unknown', 'last_update': None}
