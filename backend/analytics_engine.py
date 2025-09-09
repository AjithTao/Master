"""
Analytics Engine for Jira Leadership Quality Tool
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AdvancedAnalyticsEngine:
    """Advanced Analytics Engine for generating comprehensive Jira analytics"""
    
    def __init__(self, ai_engine, jira_client):
        self.ai_engine = ai_engine
        self.jira_client = jira_client
    
    async def generate_comprehensive_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive analytics from Jira data"""
        try:
            logger.info("Generating comprehensive analytics...")
            
            # Get basic project information
            project_keys = await self.jira_client.get_project_keys()
            
            # Initialize analytics structure
            analytics = {
                'summary': {
                    'total_projects': len(project_keys),
                    'total_stories': 0,
                    'total_defects': 0,
                    'total_tasks': 0,
                    'total_issues': 0,
                    'total_assignees': 0
                },
                'projects': {},
                'current_sprint': None,
                'generated_at': datetime.now().isoformat()
            }
            
            # Get assignees from all projects
            all_assignees = set()
            
            # Process each project
            for project_key in project_keys:
                try:
                    # Get project issues count
                    project_jql = f"project = {project_key}"
                    total_count = await self.jira_client.count(project_jql)
                    
                    # Get story count
                    story_jql = f"project = {project_key} AND issuetype = Story"
                    story_count = await self.jira_client.count(story_jql)
                    
                    # Get defect count
                    defect_jql = f"project = {project_key} AND issuetype in (Bug, Defect)"
                    defect_count = await self.jira_client.count(defect_jql)
                    
                    # Get task count
                    task_jql = f"project = {project_key} AND issuetype = Task"
                    task_count = await self.jira_client.count(task_jql)
                    
                    # Get assignees for this project
                    project_assignees = await self.jira_client.get_assignees_for_project(project_key)
                    all_assignees.update(project_assignees)
                    
                    # Store project data
                    analytics['projects'][project_key] = {
                        'name': project_key,
                        'stories': story_count,
                        'defects': defect_count,
                        'tasks': task_count,
                        'total_issues': total_count,
                        'assignee_count': len(project_assignees),
                        'assignees': list(project_assignees)
                    }
                    
                    # Update summary totals
                    analytics['summary']['total_stories'] += story_count
                    analytics['summary']['total_defects'] += defect_count
                    analytics['summary']['total_tasks'] += task_count
                    analytics['summary']['total_issues'] += total_count
                    
                except Exception as e:
                    logger.warning(f"Error processing project {project_key}: {e}")
                    continue
            
            # Update total assignees
            analytics['summary']['total_assignees'] = len(all_assignees)
            
            # Try to get current sprint info
            try:
                current_sprint = await self.jira_client.get_current_sprint()
                if current_sprint:
                    analytics['current_sprint'] = {
                        'name': current_sprint.get('name', 'Unknown'),
                        'state': current_sprint.get('state', 'Unknown'),
                        'startDate': current_sprint.get('startDate'),
                        'endDate': current_sprint.get('endDate')
                    }
            except Exception as e:
                logger.warning(f"Could not get current sprint info: {e}")
            
            logger.info(f"Analytics generated successfully: {analytics['summary']}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            # Return minimal analytics structure
            return {
                'summary': {
                    'total_projects': 0,
                    'total_stories': 0,
                    'total_defects': 0,
                    'total_tasks': 0,
                    'total_issues': 0,
                    'total_assignees': 0
                },
                'projects': {},
                'current_sprint': None,
                'generated_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def detect_anomalies(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in the analytics data"""
        anomalies = []
        
        try:
            summary = analytics.get('summary', {})
            
            # Check for high defect ratio
            total_stories = summary.get('total_stories', 0)
            total_defects = summary.get('total_defects', 0)
            
            if total_stories > 0:
                defect_ratio = (total_defects / total_stories) * 100
                if defect_ratio > 30:  # More than 30% defects
                    anomalies.append({
                        'type': 'high_defect_ratio',
                        'severity': 'high',
                        'message': f'High defect ratio: {defect_ratio:.1f}%',
                        'recommendation': 'Review development process and testing procedures'
                    })
            
            # Check for projects with no activity
            for project_key, project_data in analytics.get('projects', {}).items():
                if project_data.get('total_issues', 0) == 0:
                    anomalies.append({
                        'type': 'inactive_project',
                        'severity': 'medium',
                        'message': f'Project {project_key} has no issues',
                        'recommendation': 'Review if project is still active'
                    })
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
