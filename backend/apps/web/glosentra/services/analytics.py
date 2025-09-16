"""Analytics service for tracking and reporting."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from ..core.db import get_analytics_db
from ..core.chroma_integration import get_chroma_info


class AnalyticsService:
    """Service for analytics and reporting."""
    
    def __init__(self):
        self.db = get_analytics_db()
    
    def log_inference_run(self, task: str, model_path: str, timing: Dict[str, float], 
                         success: bool, error_message: str = None, image_size: int = 0):
        """Log an inference run."""
        self.db.log_inference(
            task=task,
            model_path=model_path,
            timing=timing,
            success=success,
            error_message=error_message,
            image_size=image_size
        )
        
        # Also log model usage
        if success:
            self.db.log_model_usage(task=task, model_path=model_path)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard."""
        stats = self.db.get_stats()
        recent_runs = self.db.get_recent_runs(limit=20)
        
        # Calculate trends (last 24 hours vs previous 24 hours)
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        prev_24h = last_24h - timedelta(hours=24)
        
        # This would require more complex queries in a real implementation
        # For now, we'll use the basic stats
        
        return {
            'overview': {
                'total_runs': stats['total_runs'],
                'success_rate': stats['success_rate'],
                'avg_fps': stats['avg_fps'],
                'avg_inference_time': stats['avg_inference_time_ms']
            },
            'task_breakdown': stats['task_stats'],
            'recent_runs': recent_runs,
            'chroma_info': get_chroma_info(),
            'timestamp': now.isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        stats = self.db.get_stats()
        
        # Performance thresholds
        fast_fps_threshold = 30
        slow_fps_threshold = 10
        fast_inference_threshold = 100  # ms
        slow_inference_threshold = 500  # ms
        
        avg_fps = stats['avg_fps']
        avg_inference_time = stats['avg_inference_time_ms']
        
        performance_grade = 'excellent'
        if avg_fps < slow_fps_threshold or avg_inference_time > slow_inference_threshold:
            performance_grade = 'poor'
        elif avg_fps < fast_fps_threshold or avg_inference_time > fast_inference_threshold:
            performance_grade = 'good'
        
        return {
            'grade': performance_grade,
            'avg_fps': avg_fps,
            'avg_inference_time_ms': avg_inference_time,
            'thresholds': {
                'fast_fps': fast_fps_threshold,
                'slow_fps': slow_fps_threshold,
                'fast_inference_ms': fast_inference_threshold,
                'slow_inference_ms': slow_inference_threshold
            }
        }
    
    def get_model_usage_stats(self) -> Dict[str, Any]:
        """Get model usage statistics."""
        try:
            with self.db.db_path.open('r') as f:
                # This is a simplified version - in practice you'd query the database
                return {
                    'most_used_task': 'detect',  # Would be calculated from actual data
                    'model_health': 'good',
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to get model usage stats: {e}")
            return {
                'most_used_task': 'unknown',
                'model_health': 'unknown',
                'last_updated': datetime.now().isoformat()
            }


# Global analytics service
_analytics_service = AnalyticsService()


def get_analytics_service() -> AnalyticsService:
    """Get global analytics service."""
    return _analytics_service
