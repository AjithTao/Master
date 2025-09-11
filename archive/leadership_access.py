"""
Leadership Access Module
Provides multiple ways for leaders without Jira access to view insights
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from auth import JiraConfig
from jira_client import JiraClient

logger = logging.getLogger(__name__)

@dataclass
class LeadershipConfig:
    """Configuration for leadership access modes"""
    shared_service_account: Optional[Dict[str, str]] = None
    cached_data_enabled: bool = True
    cache_refresh_hours: int = 4
    read_only_mode: bool = True
    allowed_operations: List[str] = None

class LeadershipAccessManager:
    """Manages different access modes for leaders without direct Jira access"""
    
    def __init__(self):
        self.config = self._load_config()
        self.shared_jira_client = None
        self.cached_data = {}
        self.last_cache_update = None
        
    def _load_config(self) -> LeadershipConfig:
        """Load leadership access configuration"""
        try:
            # Check for shared service account in environment
            shared_account = None
            if all(os.getenv(key) for key in ["JIRA_SHARED_EMAIL", "JIRA_SHARED_TOKEN", "JIRA_SHARED_URL"]):
                shared_account = {
                    "email": os.getenv("JIRA_SHARED_EMAIL"),
                    "api_token": os.getenv("JIRA_SHARED_TOKEN"),
                    "base_url": os.getenv("JIRA_SHARED_URL")
                }
            
            return LeadershipConfig(
                shared_service_account=shared_account,
                cached_data_enabled=True,
                cache_refresh_hours=4,
                read_only_mode=True,
                allowed_operations=["analytics", "insights", "reports", "dashboards"]
            )
        except Exception as e:
            logger.error(f"Error loading leadership config: {e}")
            return LeadershipConfig()
    
    async def get_jira_client_for_leaders(self) -> Optional[JiraClient]:
        """Get a Jira client for leadership access using shared credentials"""
        try:
            if not self.config.shared_service_account:
                logger.warning("No shared service account configured for leadership access")
                return None
            
            if not self.shared_jira_client:
                # Create shared Jira client
                jira_config = JiraConfig(
                    base_url=self.config.shared_service_account["base_url"],
                    email=self.config.shared_service_account["email"],
                    api_token=self.config.shared_service_account["api_token"]
                )
                
                self.shared_jira_client = JiraClient(jira_config)
                await self.shared_jira_client.initialize()
                logger.info("Shared Jira client initialized for leadership access")
            
            return self.shared_jira_client
            
        except Exception as e:
            logger.error(f"Failed to create shared Jira client: {e}")
            return None
    
    async def refresh_cached_data(self, jira_client: JiraClient):
        """Refresh cached data for leadership access"""
        try:
            logger.info("Refreshing cached data for leadership access...")
            
            # Cache key project analytics
            cached_analytics = {}
            
            # Get all projects
            projects = await jira_client.get_all_projects()
            
            for project in projects:
                project_key = project.get('key', '')
                if not project_key:
                    continue
                
                try:
                    # Get project analytics
                    project_analytics = await self._get_project_analytics(jira_client, project_key)
                    cached_analytics[project_key] = project_analytics
                    
                except Exception as e:
                    logger.warning(f"Failed to cache analytics for {project_key}: {e}")
            
            # Store cached data
            self.cached_data = {
                'analytics': cached_analytics,
                'projects': projects,
                'last_updated': datetime.now().isoformat(),
                'cache_version': '1.0'
            }
            
            self.last_cache_update = datetime.now()
            
            # Optionally save to file for persistence
            await self._save_cache_to_file()
            
            logger.info(f"Cached data refreshed for {len(cached_analytics)} projects")
            
        except Exception as e:
            logger.error(f"Failed to refresh cached data: {e}")
    
    async def _get_project_analytics(self, jira_client: JiraClient, project_key: str) -> Dict[str, Any]:
        """Get analytics for a specific project"""
        try:
            # Get project issues
            jql = f'project = "{project_key}"'
            search_result = await jira_client.search(jql, max_results=1000)
            
            if isinstance(search_result, dict) and 'issues' in search_result:
                issues = search_result['issues']
            else:
                issues = []
            
            # Analyze issues
            analytics = {
                'total_issues': len(issues),
                'by_status': {},
                'by_assignee': {},
                'by_type': {},
                'by_priority': {},
                'recent_activity': 0
            }
            
            recent_date = datetime.now() - timedelta(days=30)
            
            for issue in issues:
                fields = issue.get('fields', {})
                
                # Status analysis
                status = fields.get('status', {}).get('name', 'Unknown')
                analytics['by_status'][status] = analytics['by_status'].get(status, 0) + 1
                
                # Assignee analysis
                assignee = fields.get('assignee', {})
                assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
                analytics['by_assignee'][assignee_name] = analytics['by_assignee'].get(assignee_name, 0) + 1
                
                # Type analysis
                issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
                analytics['by_type'][issue_type] = analytics['by_type'].get(issue_type, 0) + 1
                
                # Priority analysis
                priority = fields.get('priority', {}).get('name', 'Unknown')
                analytics['by_priority'][priority] = analytics['by_priority'].get(priority, 0) + 1
                
                # Recent activity
                updated = fields.get('updated', '')
                if updated:
                    try:
                        updated_date = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                        if updated_date > recent_date:
                            analytics['recent_activity'] += 1
                    except:
                        pass
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get analytics for {project_key}: {e}")
            return {}
    
    async def _save_cache_to_file(self):
        """Save cached data to file for persistence"""
        try:
            cache_file = "leadership_cache.json"
            with open(cache_file, 'w') as f:
                json.dump(self.cached_data, f, indent=2, default=str)
            logger.info(f"Cached data saved to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save cache to file: {e}")
    
    async def _load_cache_from_file(self):
        """Load cached data from file"""
        try:
            cache_file = "leadership_cache.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    self.cached_data = json.load(f)
                logger.info("Cached data loaded from file")
                return True
        except Exception as e:
            logger.warning(f"Failed to load cache from file: {e}")
        return False
    
    def is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_cache_update or not self.cached_data:
            return False
        
        cache_age = datetime.now() - self.last_cache_update
        max_age = timedelta(hours=self.config.cache_refresh_hours)
        
        return cache_age < max_age
    
    def get_cached_analytics(self, project_key: str = None) -> Dict[str, Any]:
        """Get cached analytics data"""
        if not self.cached_data:
            return {}
        
        if project_key:
            return self.cached_data.get('analytics', {}).get(project_key, {})
        else:
            return self.cached_data.get('analytics', {})
    
    def get_leadership_summary(self) -> Dict[str, Any]:
        """Get a high-level summary for leadership"""
        if not self.cached_data:
            return {"error": "No cached data available"}
        
        analytics = self.cached_data.get('analytics', {})
        
        summary = {
            'total_projects': len(analytics),
            'last_updated': self.cached_data.get('last_updated'),
            'project_health': {},
            'top_contributors': {},
            'overall_metrics': {
                'total_issues': 0,
                'completed_issues': 0,
                'in_progress_issues': 0,
                'recent_activity': 0
            }
        }
        
        # Aggregate metrics across projects
        all_assignees = {}
        
        for project_key, project_analytics in analytics.items():
            total = project_analytics.get('total_issues', 0)
            summary['overall_metrics']['total_issues'] += total
            
            # Status aggregation
            by_status = project_analytics.get('by_status', {})
            summary['overall_metrics']['completed_issues'] += by_status.get('Done', 0)
            summary['overall_metrics']['in_progress_issues'] += by_status.get('In Progress', 0)
            summary['overall_metrics']['recent_activity'] += project_analytics.get('recent_activity', 0)
            
            # Project health assessment
            if total > 0:
                done_ratio = by_status.get('Done', 0) / total
                if done_ratio > 0.8:
                    health = 'Excellent'
                elif done_ratio > 0.6:
                    health = 'Good'
                elif done_ratio > 0.4:
                    health = 'Fair'
                else:
                    health = 'Needs Attention'
                
                summary['project_health'][project_key] = {
                    'health': health,
                    'completion_rate': f"{done_ratio:.1%}",
                    'total_issues': total
                }
            
            # Aggregate assignees
            for assignee, count in project_analytics.get('by_assignee', {}).items():
                if assignee != 'Unassigned':
                    all_assignees[assignee] = all_assignees.get(assignee, 0) + count
        
        # Top contributors
        if all_assignees:
            sorted_contributors = sorted(all_assignees.items(), key=lambda x: x[1], reverse=True)
            summary['top_contributors'] = dict(sorted_contributors[:10])
        
        return summary

# Global instance
leadership_access_manager = LeadershipAccessManager()
