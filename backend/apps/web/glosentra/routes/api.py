"""API routes for Glosentra."""

import io
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from loguru import logger

from ..core.inference import run_inference
from ..core.model_registry import get_model
from ..services.analytics import get_analytics_service

api_bp = Blueprint('api', __name__)


@api_bp.route('/healthz')
def health_check():
    """Health check endpoint."""
    return jsonify({'ok': True})


@api_bp.route('/models')
def get_models():
    """Get available models and their status."""
    try:
        models = {}
        
        # Get model paths directly from config
        model_configs = {
            'detect': current_app.config.get('MODEL_DETECT', 'models/weights/yolo11n.pt'),
            'segment': current_app.config.get('MODEL_SEGMENT', 'models/weights/yolo11n-seg.pt'),
            'classify': current_app.config.get('MODEL_CLASSIFY', 'models/weights/yolo11n-cls.pt'),
            'pose': current_app.config.get('MODEL_POSE', 'models/weights/yolo11n-pose.pt')
        }
        
        for task, path in model_configs.items():
            model = get_model(task)
            models[task] = {
                'path': path,
                'loaded': model is not None,
                'task': task
            }
        
        return jsonify({
            'success': True,
            'models': models
        })
        
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/process', methods=['POST'])
def process_image():
    """Process image with specified model."""
    try:
        # Check for file
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file size
        file.seek(0, io.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {max_size // (1024*1024)}MB'
            }), 413
        
        # Get model type
        model_type = request.form.get('model_type', 'detect')
        if model_type not in ['detect', 'segment', 'classify', 'pose']:
            return jsonify({
                'success': False,
                'error': 'Invalid model type'
            }), 400
        
        # Read image bytes
        image_bytes = file.read()
        
        # Run inference
        logger.info(f"Processing {model_type} inference for {len(image_bytes)} bytes")
        result = run_inference(
            task=model_type,
            image_bytes=image_bytes,
            timeout=30
        )
        
        # Log analytics if enabled
        if current_app.config.get('ENABLE_ANALYTICS', False):
            analytics_service = get_analytics_service()
            model_configs = {
                'detect': current_app.config.get('MODEL_DETECT', 'models/weights/yolo11n.pt'),
                'segment': current_app.config.get('MODEL_SEGMENT', 'models/weights/yolo11n-seg.pt'),
                'classify': current_app.config.get('MODEL_CLASSIFY', 'models/weights/yolo11n-cls.pt'),
                'pose': current_app.config.get('MODEL_POSE', 'models/weights/yolo11n-pose.pt')
            }
            model_path = model_configs.get(model_type, 'unknown')
            
            analytics_service.log_inference_run(
                task=model_type,
                model_path=model_path,
                timing=result.get('timing', {}),
                success=result.get('success', False),
                error_message=result.get('error'),
                image_size=file_size
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@api_bp.route('/analytics/stats')
def get_analytics_stats():
    """Get analytics statistics."""
    try:
        if not current_app.config.get('ENABLE_ANALYTICS', False):
            return jsonify({
                'success': False,
                'error': 'Analytics disabled'
            }), 400
        
        analytics_service = get_analytics_service()
        dashboard_data = analytics_service.get_dashboard_data()
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/analytics', methods=['POST'])
def log_analytics():
    """Accept client-side analytics logs."""
    try:
        if not current_app.config.get('ENABLE_ANALYTICS', False):
            return jsonify({
                'success': False,
                'error': 'Analytics disabled'
            }), 400

        data = request.get_json(silent=True) or {}

        task = data.get('task', 'unknown')
        timing = data.get('timing', {})
        success = bool(data.get('success', False))

        # Determine model path based on task from config
        model_configs = {
            'detect': current_app.config.get('MODEL_DETECT', 'models/weights/yolo11n.pt'),
            'segment': current_app.config.get('MODEL_SEGMENT', 'models/weights/yolo11n-seg.pt'),
            'classify': current_app.config.get('MODEL_CLASSIFY', 'models/weights/yolo11n-cls.pt'),
            'pose': current_app.config.get('MODEL_POSE', 'models/weights/yolo11n-pose.pt')
        }
        model_path = model_configs.get(task, 'unknown')

        analytics_service = get_analytics_service()
        analytics_service.log_inference_run(
            task=task,
            model_path=model_path,
            timing=timing,
            success=success,
            error_message=None,
            image_size=0
        )

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error logging analytics: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@api_bp.route('/search')
def search_docs():
    """Search documentation."""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        from ..core.chroma_integration import search_documents
        
        results = search_documents(query, n_results=10)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error searching docs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
