"""
AI Engine for Jira Leadership Quality Tool
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIInsight:
    """Represents an AI-generated insight"""
    def __init__(self, title: str, description: str, severity: str = "info", category: str = "general"):
        self.title = title
        self.description = description
        self.severity = severity  # info, warning, critical
        self.category = category  # performance, quality, process, resource
        self.timestamp = datetime.now().isoformat()

class AdvancedAIEngine:
    """Advanced AI Engine for generating intelligent insights and recommendations"""
    
    def __init__(self, jira_client):
        self.jira_client = jira_client
    
    def generate_intelligent_response(self, query: str, analytics: Dict[str, Any]) -> str:
        """Generate intelligent response based on query and analytics data"""
        try:
            logger.info(f"Generating intelligent response for query: {query}")
            
            # Basic response based on analytics
            summary = analytics.get('summary', {})
            projects = analytics.get('projects', {})
            
            response_parts = []
            
            # Add summary insights
            if summary.get('total_projects', 0) > 0:
                response_parts.append(f"📊 **Project Overview**: You have {summary['total_projects']} active projects with {summary['total_issues']} total issues.")
            
            if summary.get('total_assignees', 0) > 0:
                response_parts.append(f"👥 **Team Size**: {summary['total_assignees']} team members are actively working on projects.")
            
            # Add project-specific insights
            if projects:
                response_parts.append("\n📈 **Project Breakdown**:")
                for project_key, project_data in projects.items():
                    stories = project_data.get('stories', 0)
                    defects = project_data.get('defects', 0)
                    tasks = project_data.get('tasks', 0)
                    response_parts.append(f"• **{project_key}**: {stories} stories, {defects} defects, {tasks} tasks")
            
            # Add quality insights
            total_stories = summary.get('total_stories', 0)
            total_defects = summary.get('total_defects', 0)
            if total_stories > 0:
                defect_ratio = (total_defects / total_stories) * 100
                if defect_ratio > 30:
                    response_parts.append(f"\n⚠️ **Quality Alert**: High defect ratio of {defect_ratio:.1f}%. Consider reviewing development processes.")
                elif defect_ratio < 10:
                    response_parts.append(f"\n✅ **Quality Excellence**: Low defect ratio of {defect_ratio:.1f}%. Great work!")
            
            # Add recommendations
            response_parts.append("\n💡 **Recommendations**:")
            if total_stories > 0 and total_defects > 0:
                response_parts.append("• Focus on improving code quality and testing processes")
                response_parts.append("• Consider implementing more thorough code reviews")
            
            if summary.get('total_assignees', 0) > 5:
                response_parts.append("• Consider breaking down large teams into smaller, focused groups")
            
            response_parts.append("• Regular sprint retrospectives can help identify process improvements")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error generating intelligent response: {e}")
            return f"I apologize, but I encountered an error while generating insights: {str(e)}"
    
    def generate_insights(self, analytics: Dict[str, Any]) -> List[AIInsight]:
        """Generate AI insights from analytics data"""
        insights = []
        
        try:
            summary = analytics.get('summary', {})
            projects = analytics.get('projects', {})
            
            # Quality insights
            total_stories = summary.get('total_stories', 0)
            total_defects = summary.get('total_defects', 0)
            
            if total_stories > 0:
                defect_ratio = (total_defects / total_stories) * 100
                if defect_ratio > 30:
                    insights.append(AIInsight(
                        "High Defect Ratio",
                        f"Your defect ratio is {defect_ratio:.1f}%, which is above the recommended 20% threshold.",
                        "warning",
                        "quality"
                    ))
                elif defect_ratio < 10:
                    insights.append(AIInsight(
                        "Excellent Quality",
                        f"Your defect ratio is {defect_ratio:.1f}%, indicating excellent code quality.",
                        "info",
                        "quality"
                    ))
            
            # Team size insights
            total_assignees = summary.get('total_assignees', 0)
            if total_assignees > 8:
                insights.append(AIInsight(
                    "Large Team Size",
                    f"With {total_assignees} team members, consider breaking into smaller, focused teams for better coordination.",
                    "info",
                    "resource"
                ))
            
            # Project activity insights
            inactive_projects = []
            for project_key, project_data in projects.items():
                if project_data.get('total_issues', 0) == 0:
                    inactive_projects.append(project_key)
            
            if inactive_projects:
                insights.append(AIInsight(
                    "Inactive Projects",
                    f"Projects {', '.join(inactive_projects)} have no recent activity. Consider reviewing their status.",
                    "warning",
                    "process"
                ))
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append(AIInsight(
                "Analysis Error",
                f"Unable to generate insights due to: {str(e)}",
                "critical",
                "process"
            ))
        
        return insights
