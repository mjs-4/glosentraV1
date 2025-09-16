#!/usr/bin/env python3
"""
Glosentra Development Server Runner
One-command setup and run for development environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    if sys.version_info < (3, 11):
        print("Error: Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def setup_virtual_environment():
    """Setup virtual environment if it doesn't exist."""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv .venv")
    
    # Determine activation script path
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    return python_exe, pip_exe


def install_dependencies(python_exe, pip_exe):
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Upgrade pip
    print("Upgrading pip...")
    run_command(f'"{python_exe}" -m pip install -U pip')
    
    # Install ultralytics in editable mode
    print("Installing ultralytics in editable mode...")
    run_command(f'"{pip_exe}" install -e .')
    
    # Install web app dependencies
    print("Installing web app dependencies...")
    run_command(f'"{pip_exe}" install -r apps/web/requirements.txt')


def setup_environment():
    """Setup environment file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("Creating .env file from template...")
            env_file.write_text(env_example.read_text())
        else:
            print("Creating default .env file...")
            default_env = """FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=apps/web/glosentra/uploads
MAX_CONTENT_LENGTH=16777216
CHROMA_DB_PATH=data/chroma_db
ENABLE_ANALYTICS=True

MODEL_DETECT=models/weights/yolo11n.pt
MODEL_SEGMENT=models/weights/yolo11n-seg.pt
MODEL_CLASSIFY=models/weights/yolo11n-cls.pt
MODEL_POSE=models/weights/yolo11n-pose.pt
"""
            env_file.write_text(default_env)
    
    print("✓ Environment file ready")


def create_directories():
    """Create necessary directories."""
    directories = [
        "apps/web/glosentra/uploads",
        "apps/web/glosentra/logs",
        "models/weights",
        "data/chroma_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created")


def download_models(python_exe):
    """Download YOLO models if they don't exist."""
    print("Checking for YOLO models...")
    
    models = [
        "yolo11n.pt",
        "yolo11n-seg.pt", 
        "yolo11n-cls.pt",
        "yolo11n-pose.pt"
    ]
    
    models_dir = Path("models/weights")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    for model in models:
        model_path = models_dir / model
        if not model_path.exists():
            print(f"Downloading {model}...")
            download_cmd = f'"{python_exe}" -c "from ultralytics import YOLO; YOLO(\'{model}\')"'
            run_command(download_cmd)
            
            # Move downloaded model to weights directory
            if Path(model).exists():
                Path(model).rename(model_path)
                print(f"✓ Downloaded {model}")
        else:
            print(f"✓ {model} already exists")


def start_server(python_exe):
    """Start the development server."""
    print("\n" + "="*60)
    print("🚀 Starting Glosentra Development Server")
    print("="*60)
    
    # Set environment variables
    env = os.environ.copy()
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "True"
    
    # Determine server command based on platform
    if platform.system() == "Windows":
        # Use waitress on Windows
        server_cmd = f'"{python_exe}" -m waitress --port=5000 apps.web.app:app'
    else:
        # Use gunicorn on Unix-like systems
        server_cmd = f'"{python_exe}" -m gunicorn -k gthread -w 2 --threads 4 -b 0.0.0.0:5000 apps.web.app:app'
    
    print(f"Server command: {server_cmd}")
    print("\n📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("\n" + "="*60)
    
    try:
        # Start the server (this will block)
        subprocess.run(server_cmd, shell=True, env=env, check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("🚀 Glosentra Development Setup")
    print("="*40)
    
    # Check Python version
    check_python_version()
    
    # Setup virtual environment
    python_exe, pip_exe = setup_virtual_environment()
    print("✓ Virtual environment ready")
    
    # Install dependencies
    install_dependencies(python_exe, pip_exe)
    print("✓ Dependencies installed")
    
    # Setup environment
    setup_environment()
    
    # Create directories
    create_directories()
    
    # Download models
    download_models(python_exe)
    
    # Start server
    start_server(python_exe)


if __name__ == "__main__":
    main()
