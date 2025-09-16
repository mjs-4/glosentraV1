#!/usr/bin/env python3
"""
Glosentra System Diagnostics
Check system configuration, dependencies, and model loading
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
import time


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_section(title):
    """Print a section header."""
    print(f"\n📋 {title}")
    print("-" * 40)


def check_python_info():
    """Check Python version and environment."""
    print_section("Python Environment")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Processor: {platform.processor()}")
    print(f"CPU Count: {os.cpu_count()}")
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
    else:
        print("⚠️ Not running in virtual environment")


def check_dependencies():
    """Check required dependencies."""
    print_section("Dependencies")
    
    required_packages = [
        'flask',
        'ultralytics', 
        'torch',
        'opencv-python',
        'pillow',
        'numpy',
        'chromadb',
        'loguru',
        'waitress',
        'gunicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"✓ opencv-python: {cv2.__version__}")
            elif package == 'pillow':
                import PIL
                print(f"✓ pillow: {PIL.__version__}")
            elif package == 'ultralytics':
                import ultralytics
                print(f"✓ ultralytics: {ultralytics.__version__}")
            elif package == 'torch':
                import torch
                print(f"✓ torch: {torch.__version__}")
            elif package == 'numpy':
                import numpy
                print(f"✓ numpy: {numpy.__version__}")
            elif package == 'flask':
                import flask
                print(f"✓ flask: {flask.__version__}")
            elif package == 'chromadb':
                import chromadb
                print(f"✓ chromadb: {chromadb.__version__}")
            elif package == 'loguru':
                import loguru
                # loguru may not expose __version__ consistently; fall back to metadata
                try:
                    version = loguru.__version__
                except AttributeError:
                    from importlib.metadata import version as pkg_version
                    version = pkg_version('loguru')
                print(f"✓ loguru: {version}")
            elif package == 'waitress':
                import waitress  # noqa: F401
                try:
                    version = waitress.__version__  # type: ignore[attr-defined]
                except Exception:
                    from importlib.metadata import version as pkg_version
                    version = pkg_version('waitress')
                print(f"✓ waitress: {version}")
            elif package == 'gunicorn':
                import gunicorn  # noqa: F401
                try:
                    version = gunicorn.__version__  # type: ignore[attr-defined]
                except Exception:
                    from importlib.metadata import version as pkg_version
                    version = pkg_version('gunicorn')
                print(f"✓ gunicorn: {version}")
        except ImportError:
            print(f"❌ {package}: Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r apps/web/requirements.txt")
    else:
        print("\n✓ All required packages installed")


def check_gpu_support():
    """Check GPU/CUDA support."""
    print_section("GPU Support")
    
    try:
        import torch
        
        print(f"PyTorch CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA Version: {torch.version.cuda}")
            print(f"cuDNN Version: {torch.backends.cudnn.version()}")
            print(f"GPU Count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        else:
            print("⚠️ CUDA not available - using CPU")
            
    except ImportError:
        print("❌ PyTorch not installed")


def check_yolo_models():
    """Check YOLO model availability."""
    print_section("YOLO Models")
    
    models_dir = Path("models/weights")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    expected_models = [
        "yolo11n.pt",
        "yolo11n-seg.pt",
        "yolo11n-cls.pt", 
        "yolo11n-pose.pt"
    ]
    
    available_models = []
    missing_models = []
    
    for model in expected_models:
        model_path = models_dir / model
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"✓ {model}: {size_mb:.1f} MB")
            available_models.append(model)
        else:
            print(f"❌ {model}: Not found")
            missing_models.append(model)
    
    if missing_models:
        print(f"\n⚠️ Missing models: {', '.join(missing_models)}")
        print("Models will be auto-downloaded on first use")
    else:
        print("\n✓ All models available")


def test_model_loading():
    """Test YOLO model loading."""
    print_section("Model Loading Test")
    
    try:
        from ultralytics import YOLO
        
        # Test loading detection model
        print("Loading YOLO detection model...")
        start_time = time.time()
        
        model = YOLO("yolo11n.pt")
        load_time = time.time() - start_time
        
        print(f"✓ Model loaded in {load_time:.2f} seconds")
        
        # Test inference
        print("Testing inference...")
        import numpy as np
        
        test_image = np.zeros((640, 640, 3), dtype=np.uint8)
        start_time = time.time()
        
        results = model.predict(test_image, verbose=False)
        inference_time = time.time() - start_time
        
        print(f"✓ Inference completed in {inference_time:.3f} seconds")
        print(f"✓ Model device: {model.device}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False


def check_directories():
    """Check required directories."""
    print_section("Directory Structure")
    
    required_dirs = [
        "apps/web/glosentra/uploads",
        "apps/web/glosentra/logs", 
        "models/weights",
        "data/chroma_db"
    ]
    
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"✓ {directory}")
        else:
            print(f"❌ {directory}: Missing")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  → Created {directory}")
            except Exception as e:
                print(f"  → Failed to create: {e}")


def check_environment():
    """Check environment configuration."""
    print_section("Environment Configuration")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✓ .env file found")
        
        # Read and display key settings
        env_content = env_file.read_text()
        lines = env_content.strip().split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('#'):
                key, value = line.split('=', 1)
                if key in ['FLASK_ENV', 'FLASK_DEBUG', 'ENABLE_ANALYTICS']:
                    print(f"  {key}: {value}")
    else:
        print("❌ .env file not found")
        print("  → Copy env.example to .env and configure")


def check_chroma_db():
    """Check ChromaDB setup."""
    print_section("ChromaDB")
    
    try:
        import chromadb
        
        db_path = os.environ.get('CHROMA_DB_PATH', 'data/chroma_db')
        print(f"Database path: {db_path}")
        
        if Path(db_path).exists():
            print("✓ ChromaDB directory exists")
            
            # Try to connect
            client = chromadb.PersistentClient(path=db_path)
            collections = client.list_collections()
            
            if collections:
                print(f"✓ Found {len(collections)} collections")
                for collection in collections:
                    print(f"  → {collection.name}: {collection.count()} documents")
            else:
                print("⚠️ No collections found")
                print("  → Run: python scripts/ingest_docs.py")
        else:
            print("⚠️ ChromaDB directory not found")
            print("  → Will be created on first use")
            
    except ImportError:
        print("❌ ChromaDB not installed")


def check_performance():
    """Check system performance."""
    print_section("Performance Check")
    
    try:
        import torch
        import numpy as np
        from ultralytics import YOLO
        
        # CPU performance test
        print("CPU performance test...")
        start_time = time.time()
        
        # Simple matrix operations
        a = np.random.rand(1000, 1000)
        b = np.random.rand(1000, 1000)
        c = np.dot(a, b)
        
        cpu_time = time.time() - start_time
        print(f"✓ CPU matrix multiplication: {cpu_time:.3f} seconds")
        
        # GPU performance test (if available)
        if torch.cuda.is_available():
            print("GPU performance test...")
            start_time = time.time()
            
            a_gpu = torch.randn(1000, 1000, device='cuda')
            b_gpu = torch.randn(1000, 1000, device='cuda')
            c_gpu = torch.matmul(a_gpu, b_gpu)
            torch.cuda.synchronize()
            
            gpu_time = time.time() - start_time
            print(f"✓ GPU matrix multiplication: {gpu_time:.3f} seconds")
            print(f"✓ GPU speedup: {cpu_time/gpu_time:.1f}x")
        else:
            print("⚠️ GPU not available for performance test")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")


def run_diagnostics():
    """Run all diagnostics."""
    print_header("GLOSENTRA SYSTEM DIAGNOSTICS")
    print("This tool checks your system configuration and dependencies.")
    
    # Run all diagnostic checks
    check_python_info()
    check_dependencies()
    check_gpu_support()
    check_yolo_models()
    test_model_loading()
    check_directories()
    check_environment()
    check_chroma_db()
    check_performance()
    
    print_header("DIAGNOSTICS COMPLETE")
    print("If you see any ❌ or ⚠️ warnings above, please address them before running Glosentra.")
    print("\nTo start Glosentra:")
    print("  Development: python scripts/run_dev.py")
    print("  Production:  python scripts/run_prod.py")


if __name__ == "__main__":
    run_diagnostics()
