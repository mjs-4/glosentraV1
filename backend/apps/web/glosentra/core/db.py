"""SQLite database with WAL mode and background writer."""

import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from queue import Queue, Empty
from loguru import logger


class AnalyticsDB:
    """Thread-safe SQLite database for analytics."""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_queue = Queue()
        self._stop_event = threading.Event()
        self._writer_thread = None
        self._init_database()
        self._start_background_writer()
    
    def _init_database(self):
        """Initialize database with WAL mode."""
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=1000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Create tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inference_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    task TEXT NOT NULL,
                    model_path TEXT,
                    inference_time_ms REAL,
                    total_time_ms REAL,
                    fps REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    image_size_bytes INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    task TEXT NOT NULL,
                    model_path TEXT,
                    run_count INTEGER DEFAULT 1
                )
            """)
            
            conn.commit()
    
    def _start_background_writer(self):
        """Start background thread for database writes."""
        self._writer_thread = threading.Thread(target=self._background_writer, daemon=True)
        self._writer_thread.start()
    
    def _background_writer(self):
        """Background thread that processes write queue."""
        while not self._stop_event.is_set():
            try:
                # Get batch of writes (up to 100 or wait 1 second)
                writes = []
                try:
                    writes.append(self._write_queue.get(timeout=1.0))
                    # Try to get more writes without blocking
                    while len(writes) < 100:
                        try:
                            writes.append(self._write_queue.get_nowait())
                        except Empty:
                            break
                except Empty:
                    continue
                
                # Execute batch write
                if writes:
                    self._execute_batch_write(writes)
                
            except Exception as e:
                logger.error(f"Background writer error: {e}")
    
    def _execute_batch_write(self, writes: List[Dict[str, Any]]):
        """Execute batch of database writes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                
                for write in writes:
                    if write['table'] == 'inference_runs':
                        conn.execute("""
                            INSERT INTO inference_runs 
                            (task, model_path, inference_time_ms, total_time_ms, fps, success, error_message, image_size_bytes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            write['data']['task'],
                            write['data']['model_path'],
                            write['data']['inference_time_ms'],
                            write['data']['total_time_ms'],
                            write['data']['fps'],
                            write['data']['success'],
                            write['data']['error_message'],
                            write['data']['image_size_bytes']
                        ))
                    elif write['table'] == 'model_usage':
                        conn.execute("""
                            INSERT INTO model_usage (task, model_path)
                            VALUES (?, ?)
                        """, (
                            write['data']['task'],
                            write['data']['model_path']
                        ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Batch write error: {e}")
    
    def log_inference(self, task: str, model_path: str, timing: Dict[str, float], 
                     success: bool, error_message: Optional[str] = None, 
                     image_size: int = 0):
        """Log inference run (async)."""
        if self._write_queue.qsize() > 1000:  # Prevent memory buildup
            logger.warning("Analytics queue is full, dropping writes")
            return
        
        write_data = {
            'table': 'inference_runs',
            'data': {
                'task': task,
                'model_path': model_path,
                'inference_time_ms': timing.get('inference_ms', 0),
                'total_time_ms': timing.get('total_ms', 0),
                'fps': timing.get('fps', 0),
                'success': success,
                'error_message': error_message,
                'image_size_bytes': image_size
            }
        }
        
        try:
            self._write_queue.put(write_data, timeout=0.1)
        except:
            pass  # Drop if queue is full
    
    def log_model_usage(self, task: str, model_path: str):
        """Log model usage (async)."""
        write_data = {
            'table': 'model_usage',
            'data': {
                'task': task,
                'model_path': model_path
            }
        }
        
        try:
            self._write_queue.put(write_data, timeout=0.1)
        except:
            pass  # Drop if queue is full
    
    def get_recent_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent inference runs."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM inference_runs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting recent runs: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get analytics statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total runs
                total_runs = conn.execute("SELECT COUNT(*) FROM inference_runs").fetchone()[0]
                
                # Success rate
                success_runs = conn.execute("SELECT COUNT(*) FROM inference_runs WHERE success = 1").fetchone()[0]
                success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0
                
                # Average FPS
                avg_fps = conn.execute("SELECT AVG(fps) FROM inference_runs WHERE success = 1 AND fps > 0").fetchone()[0]
                avg_fps = avg_fps or 0
                
                # Average inference time
                avg_inference_time = conn.execute("SELECT AVG(inference_time_ms) FROM inference_runs WHERE success = 1").fetchone()[0]
                avg_inference_time = avg_inference_time or 0
                
                # Task breakdown
                task_stats = {}
                cursor = conn.execute("""
                    SELECT task, COUNT(*) as count, AVG(fps) as avg_fps 
                    FROM inference_runs 
                    WHERE success = 1 
                    GROUP BY task
                """)
                
                for row in cursor.fetchall():
                    task_stats[row[0]] = {
                        'count': row[1],
                        'avg_fps': row[2] or 0
                    }
                
                return {
                    'total_runs': total_runs,
                    'success_rate': round(success_rate, 2),
                    'avg_fps': round(avg_fps, 2),
                    'avg_inference_time_ms': round(avg_inference_time, 2),
                    'task_stats': task_stats
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'total_runs': 0,
                'success_rate': 0,
                'avg_fps': 0,
                'avg_inference_time_ms': 0,
                'task_stats': {}
            }
    
    def shutdown(self):
        """Shutdown database and background writer."""
        self._stop_event.set()
        if self._writer_thread:
            self._writer_thread.join(timeout=5)


# Global database instance
_analytics_db = None


def get_analytics_db() -> AnalyticsDB:
    """Get global analytics database instance."""
    global _analytics_db
    if _analytics_db is None:
        _analytics_db = AnalyticsDB()
    return _analytics_db


def shutdown_analytics_db():
    """Shutdown analytics database."""
    global _analytics_db
    if _analytics_db:
        _analytics_db.shutdown()
        _analytics_db = None
