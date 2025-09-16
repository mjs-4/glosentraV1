#!/usr/bin/env python3
"""
Glosentra Documentation Ingestion Script
Populate ChromaDB with documentation for search functionality
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any


def add_project_root_to_path():
    """Add project root to Python path."""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))


def get_sample_docs() -> List[Dict[str, Any]]:
    """Get sample documentation content."""
    return [
        {
            "content": """
# YOLO Object Detection

YOLO (You Only Look Once) is a state-of-the-art, real-time object detection system. 
It's incredibly fast and accurate, making it perfect for real-time applications.

## Key Features
- Real-time detection
- High accuracy
- Multiple object classes
- Fast inference

## Usage Example
```python
from ultralytics import YOLO
model = YOLO('yolo11n.pt')
results = model.predict('image.jpg')
```

## Classes Supported
YOLO v11 supports 80 object classes including:
- person, car, truck, bus
- cat, dog, horse, cow
- chair, table, laptop, phone
- And many more...
            """,
            "metadata": {
                "title": "Object Detection Guide",
                "category": "detection",
                "tags": ["yolo", "detection", "objects", "real-time"]
            }
        },
        {
            "content": """
# Instance Segmentation

Instance segmentation goes beyond object detection by providing pixel-level masks 
for each detected object instance. This is perfect for applications requiring 
precise object boundaries.

## Key Features
- Pixel-perfect segmentation
- Individual instance masks
- High precision
- Advanced post-processing

## Use Cases
- Medical imaging
- Robotics
- Autonomous vehicles
- Content creation

## Usage Example
```python
from ultralytics import YOLO
model = YOLO('yolo11n-seg.pt')
results = model.predict('image.jpg')
masks = results[0].masks
```

## Output Format
Each mask is returned as a binary array with the same dimensions as the input image.
            """,
            "metadata": {
                "title": "Instance Segmentation Guide",
                "category": "segmentation",
                "tags": ["segmentation", "masks", "pixel-perfect", "instances"]
            }
        },
        {
            "content": """
# Image Classification

Image classification assigns a single label to an entire image from a predefined 
set of categories. YOLO classification models are trained on ImageNet and support 
thousands of classes.

## Key Features
- Multi-class classification
- High accuracy
- Fast inference
- Large class vocabulary

## Supported Classes
YOLO classification models support 1000+ ImageNet classes including:
- Animals (cat, dog, bird, fish)
- Vehicles (car, truck, motorcycle)
- Objects (book, phone, computer)
- And many more...

## Usage Example
```python
from ultralytics import YOLO
model = YOLO('yolo11n-cls.pt')
results = model.predict('image.jpg')
top5 = results[0].probs.top5
```

## Output Format
Results include confidence scores for the top-5 predicted classes.
            """,
            "metadata": {
                "title": "Image Classification Guide",
                "category": "classification",
                "tags": ["classification", "imagenet", "categories", "labels"]
            }
        },
        {
            "content": """
# Pose Estimation

Pose estimation detects human body keypoints in images and videos. It's perfect 
for applications like fitness tracking, motion analysis, and interactive systems.

## Key Features
- 17 body keypoints
- Real-time processing
- Multi-person support
- High accuracy

## Keypoints Detected
- Head: nose, left/right eye, left/right ear
- Torso: neck, left/right shoulder, left/right hip
- Arms: left/right elbow, left/right wrist
- Legs: left/right knee, left/right ankle

## Usage Example
```python
from ultralytics import YOLO
model = YOLO('yolo11n-pose.pt')
results = model.predict('image.jpg')
keypoints = results[0].keypoints
```

## Use Cases
- Fitness applications
- Motion capture
- Sports analysis
- Interactive games
            """,
            "metadata": {
                "title": "Pose Estimation Guide",
                "category": "pose",
                "tags": ["pose", "keypoints", "human", "body", "tracking"]
            }
        },
        {
            "content": """
# Fine-tuning YOLO Models

Fine-tuning allows you to customize pre-trained YOLO models for your specific 
use case. This typically results in better performance on your data while 
requiring less training data than training from scratch.

## When to Fine-tune
- Custom object detection
- Domain-specific applications
- Specialized classification
- Edge case optimization

## Dataset Requirements
- Minimum 100 images per class
- Balanced class distribution
- High-quality annotations
- Diverse backgrounds

## Training Process
1. Prepare dataset in YOLO format
2. Create dataset.yaml configuration
3. Configure training parameters
4. Start training process
5. Evaluate results

## Example Training
```python
from ultralytics import YOLO
model = YOLO('yolo11n.pt')
results = model.train(
    data='custom_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)
```
            """,
            "metadata": {
                "title": "Fine-tuning Guide",
                "category": "training",
                "tags": ["fine-tuning", "training", "custom", "dataset", "yolo"]
            }
        },
        {
            "content": """
# API Reference

Glosentra provides a simple REST API for computer vision tasks. All endpoints 
accept multipart/form-data for image uploads and return JSON responses.

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### Health Check
```
GET /api/healthz
```
Returns server health status.

### Process Image
```
POST /api/process
```
Process an image with specified model type.

**Parameters:**
- `image`: Image file (required)
- `model_type`: detect|segment|classify|pose (required)

**Response:**
```json
{
  "success": true,
  "predictions": {
    "boxes": [[x1, y1, x2, y2], ...],
    "classes": [0, 1, ...],
    "confidences": [0.95, 0.87, ...]
  },
  "timing": {
    "inference_ms": 45.2,
    "total_ms": 67.8,
    "fps": 22.1
  }
}
```

### Get Models
```
GET /api/models
```
Returns available models and their status.

### Analytics Stats
```
GET /api/analytics/stats
```
Returns analytics and performance statistics.
            """,
            "metadata": {
                "title": "API Reference",
                "category": "api",
                "tags": ["api", "rest", "endpoints", "documentation"]
            }
        },
        {
            "content": """
# Performance Optimization

Glosentra is designed for high-performance computer vision inference. Here are 
tips to maximize performance in your applications.

## Hardware Optimization
- Use GPU acceleration when available
- Ensure sufficient RAM for model loading
- Use SSD storage for faster I/O
- Consider multi-core CPU processing

## Model Optimization
- Choose appropriate model size (n, s, m, l, x)
- Use quantization for deployment
- Batch process multiple images
- Cache model instances

## Application Optimization
- Reuse model instances
- Implement connection pooling
- Use async processing
- Monitor memory usage

## Performance Metrics
- Inference time: <100ms typical
- Throughput: 30+ FPS
- Memory usage: ~2GB for all models
- CPU usage: Optimized threading

## Troubleshooting
- Check GPU availability
- Monitor system resources
- Verify model paths
- Review error logs
            """,
            "metadata": {
                "title": "Performance Guide",
                "category": "performance",
                "tags": ["performance", "optimization", "gpu", "speed", "memory"]
            }
        }
    ]


def setup_chroma_db():
    """Setup ChromaDB database."""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Get database path from environment or use default
        db_path = os.environ.get('CHROMA_DB_PATH', 'data/chroma_db')
        
        # Create persistent client
        client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        try:
            collection = client.get_collection("documents")
            print("✓ Using existing documents collection")
        except:
            collection = client.create_collection(
                name="documents",
                metadata={"description": "Glosentra documentation"}
            )
            print("✓ Created new documents collection")
        
        return client, collection
        
    except ImportError:
        print("❌ ChromaDB not installed. Please install it with:")
        print("pip install chromadb")
        sys.exit(1)


def ingest_documents(collection, docs: List[Dict[str, Any]]):
    """Ingest documents into ChromaDB."""
    print(f"📚 Ingesting {len(docs)} documents...")
    
    documents = []
    metadatas = []
    ids = []
    
    for i, doc in enumerate(docs):
        documents.append(doc["content"])
        metadatas.append(doc["metadata"])
        ids.append(f"doc_{i}")
    
    try:
        # Add documents to collection
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print("✓ Documents ingested successfully")
        
        # Verify ingestion
        count = collection.count()
        print(f"✓ Collection now contains {count} documents")
        
    except Exception as e:
        print(f"❌ Error ingesting documents: {e}")
        sys.exit(1)


def test_search(collection):
    """Test search functionality."""
    print("\n🔍 Testing search functionality...")
    
    test_queries = [
        "How do I detect objects?",
        "What is segmentation?",
        "How to fine-tune models?",
        "API documentation",
        "Performance optimization"
    ]
    
    for query in test_queries:
        try:
            results = collection.query(
                query_texts=[query],
                n_results=2
            )
            
            print(f"Query: '{query}'")
            if results['documents'] and results['documents'][0]:
                print(f"  → Found {len(results['documents'][0])} results")
                print(f"  → Top result: {results['metadatas'][0][0]['title']}")
            else:
                print("  → No results found")
            print()
            
        except Exception as e:
            print(f"  ❌ Search error: {e}")


def main():
    """Main entry point."""
    print("📚 Glosentra Documentation Ingestion")
    print("="*50)
    
    # Add project root to path
    add_project_root_to_path()
    
    # Setup ChromaDB
    client, collection = setup_chroma_db()
    
    # Get sample documents
    docs = get_sample_docs()
    
    # Ingest documents
    ingest_documents(collection, docs)
    
    # Test search
    test_search(collection)
    
    print("\n✅ Documentation ingestion completed!")
    print("You can now use the search functionality in the Docs page.")


if __name__ == "__main__":
    main()
