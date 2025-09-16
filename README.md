# 🚀 Glosentra - Advanced Computer Vision Platform

<div align="center">

![Glosentra Logo](https://img.shields.io/badge/Glosentra-Advanced%20CV-purple?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge&logo=flask)
![YOLO](https://img.shields.io/badge/YOLO-v11-red?style=for-the-badge&logo=yolo)
![License](https://img.shields.io/badge/License-AGPL--3.0-orange?style=for-the-badge)

**Deploy state-of-the-art computer vision models with a beautiful modern interface**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🎯 Features](#-features) • [🛠️ API](#-api) • [📊 Demo](#-demo)

</div>

---

## ✨ Overview

**Glosentra** is a modern, high-performance computer vision platform built on YOLO v11 and Flask. Deploy state-of-the-art object detection, segmentation, classification, and pose estimation with a beautiful dark neo-glass UI and enterprise-grade performance.

### 🎯 Key Capabilities

- **🎯 Four AI Tasks**: Object Detection, Instance Segmentation, Image Classification, Pose Estimation
- **⚡ Real-time Inference**: Sub-100ms processing with GPU acceleration
- **🎨 Modern UI**: Dark neo-glass design with purple→pink accents
- **🚀 One-Command Setup**: Automated development and production deployment
- **📊 Analytics Dashboard**: Performance monitoring and usage statistics
- **🔍 Document Search**: ChromaDB-powered documentation search
- **🛠️ Fine-tuning Support**: Custom model training and deployment
- **📱 Responsive Design**: Works on desktop, tablet, and mobile

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (required)
- **4GB+ RAM** (8GB+ recommended)
- **GPU with CUDA support** (optional, for faster inference)

### One-Command Setup

```bash
# Clone the repository
git clone <repository-url>
cd glosentra

# Run the development server (automatically sets up everything)
python scripts/run_dev.py
```

That's it! The script will automatically:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Download YOLO models
- ✅ Start the development server
- ✅ Open at `http://localhost:5000`

---

## 🛠️ Manual Installation

If you prefer manual setup:

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
python -m pip install -U pip
pip install -e .
pip install -r apps/web/requirements.txt

# 4. Setup environment
cp env.example .env

# 5. Start development server
python scripts/run_dev.py
```

---

## 🎯 Usage

### Web Interface

Navigate to `http://localhost:5000` to access the web interface:

1. **🏠 Home**: Overview and feature cards
2. **🚀 Deploy**: Upload images for processing
   - **Object Detection**: Detect and localize objects
   - **Instance Segmentation**: Pixel-perfect object masks
   - **Image Classification**: Categorize images
   - **Pose Estimation**: Human pose keypoints
3. **📹 Real-time**: Live webcam processing
4. **📊 Analytics**: Performance dashboard
5. **📚 Docs**: Searchable documentation
6. **🔧 Fine-Tune**: Custom model training guide

### API Usage

**Process an image:**
```bash
curl -X POST http://localhost:5000/api/process \
  -F "image=@your_image.jpg" \
  -F "model_type=detect"
```

**Response:**
```json
{
  "success": true,
  "predictions": {
    "boxes": [[x1, y1, x2, y2], ...],
    "classes": [0, 1, ...],
    "confidences": [0.95, 0.87, ...],
    "class_names": ["person", "car", ...]
  },
  "timing": {
    "inference_ms": 45.2,
    "total_ms": 67.8,
    "fps": 22.1
  }
}
```

### Python SDK

```python
import requests

# Process image
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/process',
        files={'image': f},
        data={'model_type': 'detect'}
    )
    
result = response.json()
print(f"Detected {len(result['predictions']['boxes'])} objects")
```

---

## 🏗️ Project Structure

```
glosentra/
├── 📁 apps/
│   └── web/                          # Flask web application
│       ├── glosentra/                # Main application package
│       │   ├── __init__.py           # App factory
│       │   ├── config.py             # Configuration management
│       │   ├── core/                 # Core modules
│       │   │   ├── chroma_integration.py  # Vector database
│       │   │   ├── db.py             # Database operations
│       │   │   ├── inference.py      # Model inference
│       │   │   └── model_registry.py # Model management
│       │   ├── routes/               # Flask routes
│       │   │   ├── api.py            # API endpoints
│       │   │   └── pages.py          # Web pages
│       │   ├── services/             # Business logic
│       │   │   └── analytics.py      # Analytics service
│       │   ├── templates/            # Jinja2 templates
│       │   ├── static/               # CSS/JS assets
│       │   └── uploads/              # File uploads
│       ├── app.py                    # Application entry point
│       └── requirements.txt          # Python dependencies
├── 📁 models/weights/                # YOLO model files
├── 📁 scripts/                       # Utility scripts
│   ├── run_dev.py                    # Development server
│   ├── run_prod.py                   # Production server
│   └── ingest_docs.py                # Document ingestion
├── 📁 tests/                         # Test suite
├── 📁 data/chroma_db/                # Vector database
├── 📁 dist/                          # Static site build
├── 📄 package.json                   # Node.js build config
├── 📄 pyproject.toml                 # Python package config
└── 📄 README.md                      # This file
```

---

## 🚀 Production Deployment

### Quick Production Setup

```bash
python scripts/run_prod.py
```

### Manual Production Setup

```bash
# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Use production server
python -m gunicorn -k gthread -w 4 --threads 8 \
  --worker-connections 1000 -b 0.0.0.0:5000 \
  apps.web.app:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r apps/web/requirements.txt
RUN pip install -e .

EXPOSE 5000
CMD ["python", "scripts/run_prod.py"]
```

### Static Site Deployment (GitHub Pages)

```bash
# Build static site
npm run build

# Deploy to GitHub Pages
npm run deploy
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# File Upload
UPLOAD_FOLDER=apps/web/glosentra/uploads
MAX_CONTENT_LENGTH=16777216

# Database
CHROMA_DB_PATH=data/chroma_db
ENABLE_ANALYTICS=True

# Model Paths
MODEL_DETECT=models/weights/yolo11n.pt
MODEL_SEGMENT=models/weights/yolo11n-seg.pt
MODEL_CLASSIFY=models/weights/yolo11n-cls.pt
MODEL_POSE=models/weights/yolo11n-pose.pt
```

### Model Configuration

Place custom YOLO models in `models/weights/`:
- `yolo11n.pt` - Object detection
- `yolo11n-seg.pt` - Instance segmentation  
- `yolo11n-cls.pt` - Image classification
- `yolo11n-pose.pt` - Pose estimation

---

## 📊 Performance

### Benchmarks

| Task | Model | Inference Time | FPS | Accuracy |
|------|-------|----------------|-----|----------|
| Detection | YOLOv11n | ~45ms | 22 FPS | 37.3 mAP |
| Segmentation | YOLOv11n-seg | ~52ms | 19 FPS | 33.9 mAP |
| Classification | YOLOv11n-cls | ~38ms | 26 FPS | 66.6% top-1 |
| Pose | YOLOv11n-pose | ~48ms | 21 FPS | 68.5 mAP |

*Benchmarks on RTX 3080, 640px input*

### Optimization Tips

1. **GPU Acceleration**: Ensure CUDA is available for 3-5x speedup
2. **Model Selection**: Use smaller models (nano) for speed, larger for accuracy
3. **Batch Processing**: Process multiple images simultaneously
4. **Caching**: Models are pre-loaded and cached for faster inference

---

## 🧪 Testing

### Run Tests

```bash
# Smoke tests
python tests/test_web_smoke.py

# Diagnostics
python apps/web/diagnostics.py

# Manual testing
# 1. Start server: python scripts/run_dev.py
# 2. Open: http://localhost:5000
# 3. Upload image on any deploy page
# 4. Check analytics dashboard
```

---

## 🔧 Development

### Adding New Features

1. **New Routes**: Add to `apps/web/glosentra/routes/`
2. **New Templates**: Add to `apps/web/glosentra/templates/`
3. **New Models**: Add to `apps/web/glosentra/core/model_registry.py`
4. **New APIs**: Add to `apps/web/glosentra/routes/api.py`

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 🔍 Troubleshooting

### Common Issues

**"Backend not working"**
- Check if models are downloaded: `ls models/weights/`
- Verify server is running: `curl http://localhost:5000/api/healthz`
- Check logs: `tail -f apps/web/glosentra/logs/glosentra.log`

**Slow inference**
- Verify GPU support: `python -c "import torch; print(torch.cuda.is_available())"`
- Check model loading: `python apps/web/diagnostics.py`
- Monitor system resources

**Upload errors**
- Check file size (max 16MB)
- Verify file format (JPG, PNG, WebP)
- Check upload directory permissions

### Getting Help

1. Check the [documentation](http://localhost:5000/docs)
2. Run diagnostics: `python apps/web/diagnostics.py`
3. Check logs in `apps/web/glosentra/logs/`
4. Review the analytics dashboard

---

## 📄 License

This project is licensed under the **AGPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLO models
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [ChromaDB](https://www.trychroma.com/) for vector search

---

## 📞 Support

- 📧 **Email**: support@glosentra.com
- 💬 **Discord**: [Glosentra Community](https://discord.gg/glosentra)
- 📖 **Docs**: [Documentation](http://localhost:5000/docs)
- 🐛 **Issues**: [GitHub Issues](https://github.com/glosentra/glosentra/issues)

---

<div align="center">

**Glosentra** - Deploy Vision AI in Minutes ⚡

[![GitHub stars](https://img.shields.io/github/stars/glosentra/glosentra?style=social)](https://github.com/glosentra/glosentra)
[![GitHub forks](https://img.shields.io/github/forks/glosentra/glosentra?style=social)](https://github.com/glosentra/glosentra)
[![GitHub watchers](https://img.shields.io/github/watchers/glosentra/glosentra?style=social)](https://github.com/glosentra/glosentra)

</div>