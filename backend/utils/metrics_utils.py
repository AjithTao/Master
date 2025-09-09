from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import re
from datetime import datetime, timezone
import math

@dataclass
class SprintMetrics:
    sprint_id: str
    sprint_name: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    total_stories: int
    completed_stories: int
    in_progress_stories: int
    todo_stories: int
    total_story_points: float
    completed_story_points: float
    velocity: float
    completion_rate: float
    defect_count: int
    defect_ratio: float
    spillover_count: int
    spillover_rate: float

@dataclass
class VelocityForecast:
    current_velocity: float
    projected_velocity: float
    burn_rate: float
    days_remaining: int
    stories_remaining: int
    completion_probability: float
    confidence_level: str

@dataclass
class BandwidthAnalysis:
    team_member: str
    current_load: float
    max_capacity: float
    utilization_rate: float
    available_capacity: float
    recommended_story_points: float

def parse_sprint_number(name: Optional[str]) -> Optional[int]:
    if not name:
        return None
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else None

def to_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def find_story_points_field(fields: List[Dict[str, Any]]) -> Optional[str]:
    # Common names: "Story Points", "Story point estimate"
    for f in fields:
        name = (f.get("name") or "").lower()
        if "story point" in name:
            return f.get("id")
    return None

def get_issue_status_key(issue: Dict[str, Any]) -> str:
    f = issue.get("fields", {})
    sc = (f.get("status", {}) or {}).get("statusCategory", {}) or {}
    key = sc.get("key")
    if key:
        return key
    # fallback on name
    name = (f.get("status", {}) or {}).get("name", "")
    return "done" if name.lower() in ["done", "closed"] else "todo"

def is_done(issue: Dict[str, Any]) -> bool:
    k = get_issue_status_key(issue)
    return k == "done"

def sum_story_points(issue: Dict[str, Any], sp_field_id: Optional[str]) -> float:
    if not sp_field_id:
        return 0.0
    val = (issue.get("fields", {}) or {}).get(sp_field_id)
    try:
        return float(val) if val is not None else 0.0
    except Exception:
        return 0.0

# Simple forecasting
def _linear_regression(y: List[float]) -> tuple[float, float]:
    n = len(y)
    if n < 2:
        return 0.0, float(y[0]) if y else 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(y) / n
    num = sum((i - x_mean)*(y[i] - y_mean) for i in range(n))
    den = sum((i - x_mean)**2 for i in range(n))
    m = num / den if den else 0.0
    b = y_mean - m * x_mean
    return m, b

def _exp_smoothing(y: List[float], alpha: float = 0.45) -> float:
    if not y:
        return 0.0
    s = y[0]
    for v in y[1:]:
        s = alpha*v + (1-alpha)*s
    return s

def forecast_velocity(velocities: List[float]) -> dict:
    v = [float(x) for x in velocities if x is not None]
    if not v:
        return {"next": 0.0, "band": [0.0, 0.0], "trend": 0.0, "avg": 0.0}
    avg = sum(v)/len(v)
    m, b = _linear_regression(v)
    trend_next = m*len(v) + b
    es_next = _exp_smoothing(v, alpha=0.45)
    fused = 0.5*trend_next + 0.5*es_next

    # crude uncertainty band from residuals
    residuals = []
    for i, actual in enumerate(v):
        t = m*i + b
        es_i = _exp_smoothing(v[:i+1], 0.45)
        resid = actual - 0.5*t - 0.5*es_i
        residuals.append(resid)
    sd = math.sqrt(sum(e*e for e in residuals)/max(1, len(residuals))) if residuals else 0.0
    band = [max(0.0, fused - 1.28*sd), fused + 1.28*sd]  # ~80% band

    return {"next": round(fused, 2), "band": [round(band[0], 2), round(band[1], 2)],
            "trend": round(m, 3), "avg": round(avg, 2)}

def parse_sprint_metrics(issues: List[Dict[str, Any]], sprint_info: Dict[str, Any]) -> SprintMetrics:
    """Parse sprint metrics from issues and sprint info"""
    sprint_id = str(sprint_info.get('id', ''))
    sprint_name = sprint_info.get('name', 'Unknown Sprint')
    start_date = to_dt(sprint_info.get('startDate'))
    end_date = to_dt(sprint_info.get('endDate'))
    
    # Count stories and calculate metrics
    total_stories = len([i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Story'])
    completed_stories = len([i for i in issues if is_done(i) and i.get('fields', {}).get('issuetype', {}).get('name') == 'Story'])
    in_progress_stories = len([i for i in issues if get_issue_status_key(i) == 'indeterminate' and i.get('fields', {}).get('issuetype', {}).get('name') == 'Story'])
    todo_stories = total_stories - completed_stories - in_progress_stories
    
    # Calculate story points (simplified - would need field discovery in real implementation)
    total_story_points = sum(sum_story_points(i, None) for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Story')
    completed_story_points = sum(sum_story_points(i, None) for i in issues if is_done(i) and i.get('fields', {}).get('issuetype', {}).get('name') == 'Story')
    
    velocity = completed_story_points
    completion_rate = (completed_stories / total_stories * 100) if total_stories > 0 else 0.0
    
    # Count defects
    defect_count = len([i for i in issues if i.get('fields', {}).get('issuetype', {}).get('name') == 'Bug'])
    defect_ratio = (defect_count / len(issues) * 100) if issues else 0.0
    
    # Spillover calculation (simplified)
    spillover_count = 0  # Would need to check creation date vs sprint start
    spillover_rate = 0.0
    
    return SprintMetrics(
        sprint_id=sprint_id,
        sprint_name=sprint_name,
        start_date=start_date,
        end_date=end_date,
        total_stories=total_stories,
        completed_stories=completed_stories,
        in_progress_stories=in_progress_stories,
        todo_stories=todo_stories,
        total_story_points=total_story_points,
        completed_story_points=completed_story_points,
        velocity=velocity,
        completion_rate=completion_rate,
        defect_count=defect_count,
        defect_ratio=defect_ratio,
        spillover_count=spillover_count,
        spillover_rate=spillover_rate
    )

def forecast_velocity_wrapper(historical_velocities: List[float], current_sprint_issues: List[Dict[str, Any]]) -> VelocityForecast:
    """Forecast velocity based on historical data and current sprint progress"""
    if not historical_velocities:
        return VelocityForecast(
            current_velocity=0.0,
            projected_velocity=0.0,
            burn_rate=0.0,
            days_remaining=0,
            stories_remaining=0,
            completion_probability=0.0,
            confidence_level="low"
        )
    
    forecast_data = forecast_velocity(historical_velocities)
    current_velocity = forecast_data["avg"]
    projected_velocity = forecast_data["next"]
    
    # Calculate burn rate and remaining work
    completed_issues = len([i for i in current_sprint_issues if is_done(i)])
    total_issues = len(current_sprint_issues)
    stories_remaining = total_issues - completed_issues
    
    # Simplified burn rate calculation
    burn_rate = completed_issues / max(1, total_issues) if total_issues > 0 else 0.0
    
    # Calculate completion probability
    completion_probability = min(100.0, burn_rate * 100)
    
    # Determine confidence level
    if len(historical_velocities) >= 5:
        confidence_level = "high"
    elif len(historical_velocities) >= 3:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    return VelocityForecast(
        current_velocity=current_velocity,
        projected_velocity=projected_velocity,
        burn_rate=burn_rate,
        days_remaining=7,  # Simplified - would calculate actual days remaining
        stories_remaining=stories_remaining,
        completion_probability=completion_probability,
        confidence_level=confidence_level
    )

def analyze_bandwidth(issues: List[Dict[str, Any]]) -> List[BandwidthAnalysis]:
    """Analyze team bandwidth based on current workload"""
    # Group issues by assignee
    assignee_workload = {}
    for issue in issues:
        assignee = issue.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned')
        if assignee not in assignee_workload:
            assignee_workload[assignee] = []
        assignee_workload[assignee].append(issue)
    
    bandwidth_analysis = []
    for assignee, assignee_issues in assignee_workload.items():
        if assignee == 'Unassigned':
            continue
            
        # Calculate current load
        current_load = len(assignee_issues)
        max_capacity = 10.0  # Simplified - would be configurable
        utilization_rate = (current_load / max_capacity) * 100
        available_capacity = max(0, max_capacity - current_load)
        recommended_story_points = min(available_capacity * 2, 8.0)  # Simplified calculation
        
        bandwidth_analysis.append(BandwidthAnalysis(
            team_member=assignee,
            current_load=current_load,
            max_capacity=max_capacity,
            utilization_rate=utilization_rate,
            available_capacity=available_capacity,
            recommended_story_points=recommended_story_points
        ))
    
    return bandwidth_analysis

def generate_insights(current_metrics: SprintMetrics, forecast: Optional[VelocityForecast], bandwidth: List[BandwidthAnalysis]) -> List[str]:
    """Generate AI insights based on sprint metrics"""
    insights = []
    
    # Sprint completion insights
    if current_metrics.completion_rate < 50:
        insights.append("⚠️ Sprint completion rate is below 50%. Consider reviewing scope or adding resources.")
    elif current_metrics.completion_rate > 90:
        insights.append("✅ Excellent sprint progress! Team is on track for completion.")
    
    # Defect ratio insights
    if current_metrics.defect_ratio > 20:
        insights.append("🐛 High defect ratio detected. Consider improving quality processes.")
    
    # Velocity insights
    if forecast and forecast.confidence_level == "high":
        if forecast.projected_velocity > current_metrics.velocity * 1.2:
            insights.append("📈 Velocity trending upward. Great momentum!")
        elif forecast.projected_velocity < current_metrics.velocity * 0.8:
            insights.append("📉 Velocity declining. Review team capacity and blockers.")
    
    # Bandwidth insights
    overloaded_members = [b for b in bandwidth if b.utilization_rate > 90]
    if overloaded_members:
        insights.append(f"⚡ {len(overloaded_members)} team member(s) are overloaded. Consider redistributing work.")
    
    underutilized_members = [b for b in bandwidth if b.utilization_rate < 50]
    if underutilized_members:
        insights.append(f"💡 {len(underutilized_members)} team member(s) have available capacity. Consider additional tasks.")
    
    # Default insight if no specific insights
    if not insights:
        insights.append("📊 Sprint metrics look balanced. Continue monitoring progress.")
    
    return insights