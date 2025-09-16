"""High-performance inference engine with thread pooling."""

import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image
import cv2
from loguru import logger

from .model_registry import get_model, get_device


class InferenceEngine:
    """Thread-pooled inference engine."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or max(2, min(8, os.cpu_count() or 2))
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        logger.info(f"Initialized inference engine with {self.max_workers} workers")
    
    def run_inference(self, task: str, image_bytes: bytes, **kwargs) -> Dict[str, Any]:
        """Run inference on image bytes."""
        start_time = time.time()
        
        try:
            # Decode image
            decode_start = time.time()
            image = self._decode_image(image_bytes)
            decode_time = time.time() - decode_start
            
            # Get model
            model = get_model(task)
            if not model:
                raise ValueError(f"No model available for task: {task}")
            
            # Run inference
            infer_start = time.time()
            results = model.predict(
                image,
                imgsz=kwargs.get('imgsz', 640),
                conf=kwargs.get('conf', 0.25),
                device=get_device(),
                verbose=False
            )
            infer_time = time.time() - infer_start
            
            # Process results
            process_start = time.time()
            predictions = self._process_results(results, task)
            process_time = time.time() - process_start
            
            total_time = time.time() - start_time
            
            return {
                'success': True,
                'predictions': predictions,
                'timing': {
                    'decode_ms': round(decode_time * 1000, 2),
                    'inference_ms': round(infer_time * 1000, 2),
                    'process_ms': round(process_time * 1000, 2),
                    'total_ms': round(total_time * 1000, 2)
                },
                'fps': round(1000 / (infer_time * 1000), 2) if infer_time > 0 else 0,
                'task': task
            }
            
        except Exception as e:
            logger.error(f"Inference failed for {task}: {e}")
            return {
                'success': False,
                'error': str(e),
                'task': task
            }
    
    def _decode_image(self, image_bytes: bytes) -> np.ndarray:
        """Decode image bytes to numpy array."""
        import io
        
        # Try PIL first
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return np.array(image)
        except Exception:
            pass
        
        # Fallback to OpenCV
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is not None:
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception:
            pass
        
        raise ValueError("Failed to decode image")
    
    def _process_results(self, results, task: str) -> Dict[str, Any]:
        """Process YOLO results into JSON-serializable format."""
        if not results or len(results) == 0:
            return {'boxes': [], 'masks': [], 'classes': [], 'confidences': []}
        
        result = results[0]  # First (and typically only) result
        
        # Common fields
        output = {
            'classes': [],
            'confidences': []
        }
        
        # Task-specific processing
        if task in ['detect', 'segment', 'pose']:
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confs = result.boxes.conf.cpu().numpy()
                cls_ids = result.boxes.cls.cpu().numpy()
                
                output['boxes'] = boxes.tolist()
                output['confidences'] = confs.tolist()
                output['classes'] = cls_ids.tolist()
                
                # Add class names if available
                if hasattr(result, 'names'):
                    output['class_names'] = [result.names[int(cls_id)] for cls_id in cls_ids]
        
        if task == 'segment':
            if result.masks is not None:
                masks = result.masks.data.cpu().numpy()
                output['masks'] = masks.tolist()
        
        if task == 'pose':
            if result.keypoints is not None:
                keypoints = result.keypoints.xy.cpu().numpy()
                output['keypoints'] = keypoints.tolist()
        
        if task == 'classify':
            if result.probs is not None:
                probs = result.probs.data.cpu().numpy()
                top5_idx = np.argsort(probs)[-5:][::-1]
                output['predictions'] = [
                    {
                        'class_id': int(idx),
                        'confidence': float(probs[idx]),
                        'class_name': result.names.get(idx, f'class_{idx}')
                    }
                    for idx in top5_idx
                ]
        
        return output
    
    def run_async(self, task: str, image_bytes: bytes, timeout: int = 30, **kwargs):
        """Run inference asynchronously with timeout."""
        future = self.executor.submit(self.run_inference, task, image_bytes, **kwargs)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            logger.error(f"Inference timeout for {task}")
            return {
                'success': False,
                'error': 'Inference timeout',
                'task': task
            }
    
    def shutdown(self):
        """Shutdown the thread pool."""
        self.executor.shutdown(wait=True)


# Global inference engine
_inference_engine = InferenceEngine()


def run_inference(task: str, image_bytes: bytes, **kwargs) -> Dict[str, Any]:
    """Run inference on image bytes."""
    return _inference_engine.run_async(task, image_bytes, **kwargs)


def shutdown_inference():
    """Shutdown inference engine."""
    _inference_engine.shutdown()
