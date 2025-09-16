"""Model registry for thread-safe YOLO model management."""

import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional
import torch
from ultralytics import YOLO
from loguru import logger


class ModelRegistry:
    """Thread-safe singleton for YOLO model management."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._models: Dict[str, YOLO] = {}
            self._model_lock = threading.Lock()
            self._device = self._get_device()
            self._configure_torch()
            self._initialized = True
    
    def _configure_torch(self):
        """Configure PyTorch threading."""
        torch.set_num_threads(min(4, os.cpu_count() or 2))
        os.environ.setdefault("OMP_NUM_THREADS", "4")
        os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    
    def _get_device(self) -> str:
        """Auto-select device."""
        if torch.cuda.is_available():
            return "cuda:0"
        return "cpu"
    
    def get_model(self, task: str) -> Optional[YOLO]:
        """Get model for task, loading if necessary."""
        with self._model_lock:
            if task not in self._models:
                self._load_model(task)
            return self._models.get(task)
    
    def _load_model(self, task: str):
        """Load model for task."""
        from flask import current_app
        
        model_paths = current_app.config.get('MODEL_PATHS', {})
        model_path = model_paths.get(task)
        
        if not model_path or not Path(model_path).exists():
            logger.warning(f"Model file not found for {task}, using default")
            # Correct default filenames per Ultralytics naming
            default_map = {
                'detect': 'yolo11n.pt',
                'segment': 'yolo11n-seg.pt',
                'classify': 'yolo11n-cls.pt',
                'pose': 'yolo11n-pose.pt'
            }
            model_path = default_map.get(task, 'yolo11n.pt')
        
        try:
            logger.info(f"Loading {task} model from {model_path}")
            model = YOLO(model_path)
            self._models[task] = model
            logger.info(f"Successfully loaded {task} model")
        except Exception as e:
            logger.error(f"Failed to load {task} model: {e}")
            # Fallback to default model
            try:
                default_map = {
                    'detect': 'yolo11n.pt',
                    'segment': 'yolo11n-seg.pt',
                    'classify': 'yolo11n-cls.pt',
                    'pose': 'yolo11n-pose.pt'
                }
                default_model = default_map.get(task, 'yolo11n.pt')
                model = YOLO(default_model)
                self._models[task] = model
                logger.info(f"Loaded fallback {task} model")
            except Exception as e2:
                logger.error(f"Failed to load fallback {task} model: {e2}")
    
    def preload_models(self, tasks: List[str]):
        """Preload models with warmup inference."""
        for task in tasks:
            model = self.get_model(task)
            if model:
                try:
                    # Warmup with small image
                    import numpy as np
                    warmup_img = np.zeros((64, 64, 3), dtype=np.uint8)
                    model.predict(warmup_img, verbose=False, device=self._device)
                    logger.info(f"Warmed up {task} model")
                except Exception as e:
                    logger.error(f"Failed to warm up {task} model: {e}")
    
    def get_device(self) -> str:
        """Get current device."""
        return self._device


# Global registry instance
_registry = ModelRegistry()


def get_model(task: str) -> Optional[YOLO]:
    """Get model for task."""
    return _registry.get_model(task)


def preload_models(tasks: List[str]):
    """Preload models."""
    _registry.preload_models(tasks)


def get_device() -> str:
    """Get current device."""
    return _registry.get_device()
