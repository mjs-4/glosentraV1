"""Glosentra Flask application factory."""

import os
import threading
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from flask_caching import Cache
from loguru import logger

from .config import config
from .core.model_registry import preload_models


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    # Expose consolidated model paths for registry
    try:
        app.config['MODEL_PATHS'] = config[config_name]().get_model_paths()
    except Exception:
        app.config['MODEL_PATHS'] = {
            'detect': app.config.get('MODEL_DETECT', 'models/weights/yolo11n.pt'),
            'segment': app.config.get('MODEL_SEGMENT', 'models/weights/yolo11n-seg.pt'),
            'classify': app.config.get('MODEL_CLASSIFY', 'models/weights/yolo11n-cls.pt'),
            'pose': app.config.get('MODEL_POSE', 'models/weights/yolo11n-pose.pt')
        }
    
    # Create upload directory
    upload_dir = Path(app.config['UPLOAD_FOLDER'])
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    Compress(app)
    cache = Cache(app)
    
    # Register blueprints
    from .routes import pages_bp, api_bp
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Warm up models in background thread
    def warmup_models():
        """Preload models in background thread with app context."""
        def _preload():
            try:
                logger.info("Starting model preload...")
                # Ensure Flask application context is available during preload
                with app.app_context():
                    preload_models(['detect', 'segment', 'classify', 'pose'])
                logger.info("Model preload completed")
            except Exception as e:
                logger.error(f"Model preload failed: {e}")
        
        thread = threading.Thread(target=_preload, daemon=True)
        thread.start()
    
    # Start model preload
    warmup_models()
    
    # Configure logging
    logger.add(
        "apps/web/glosentra/logs/glosentra.log",
        rotation="1 day",
        retention="30 days",
        level="INFO"
    )
    
    return app
