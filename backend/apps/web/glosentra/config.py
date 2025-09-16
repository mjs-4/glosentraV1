"""Configuration for Glosentra Flask application."""

import os
from pathlib import Path


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SEND_FILE_MAX_AGE_DEFAULT = 86400  # 24 hours
    JSON_SORT_KEYS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'apps/web/glosentra/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Model paths
    MODEL_DETECT = os.environ.get('MODEL_DETECT', 'models/weights/yolo11n.pt')
    MODEL_SEGMENT = os.environ.get('MODEL_SEGMENT', 'models/weights/yolo11n-seg.pt')
    MODEL_CLASSIFY = os.environ.get('MODEL_CLASSIFY', 'models/weights/yolo11n-cls.pt')
    MODEL_POSE = os.environ.get('MODEL_POSE', 'models/weights/yolo11n-pose.pt')
    
    # Database settings
    CHROMA_DB_PATH = os.environ.get('CHROMA_DB_PATH', 'data/chroma_db')
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'True').lower() == 'true'
    
    # Caching
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60
    
    # Threading
    THREAD_POOL_WORKERS = max(2, min(8, os.cpu_count() or 2))
    
    def get_model_paths(self):
        """Get model paths as dictionary."""
        return {
            'detect': self.MODEL_DETECT,
            'segment': self.MODEL_SEGMENT,
            'classify': self.MODEL_CLASSIFY,
            'pose': self.MODEL_POSE
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
