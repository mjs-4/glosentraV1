"""Lazy ChromaDB integration for document search."""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import lru_cache
from loguru import logger


class ChromaIntegration:
    """Lazy ChromaDB client for document search."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._client = None
        self._collection = None
    
    @property
    def client(self):
        """Get ChromaDB client (lazy loaded)."""
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=str(self.db_path))
                logger.info(f"ChromaDB client initialized at {self.db_path}")
            except ImportError:
                logger.warning("ChromaDB not available, document search disabled")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                return None
        return self._client
    
    @property
    def collection(self):
        """Get or create documents collection."""
        if self._collection is None and self.client:
            try:
                # Try to get existing collection
                self._collection = self.client.get_collection("documents")
                logger.info("Loaded existing ChromaDB documents collection")
            except:
                try:
                    # Create new collection
                    self._collection = self.client.create_collection(
                        name="documents",
                        metadata={"description": "Glosentra documentation"}
                    )
                    logger.info("Created new ChromaDB documents collection")
                except Exception as e:
                    logger.error(f"Failed to create ChromaDB collection: {e}")
                    return None
        return self._collection
    
    def is_available(self) -> bool:
        """Check if ChromaDB is available and initialized."""
        return self.client is not None and self.collection is not None
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents."""
        if not self.is_available():
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'content': doc,
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    def add_document(self, content: str, metadata: Dict[str, Any], doc_id: Optional[str] = None):
        """Add document to collection."""
        if not self.is_available():
            return False
        
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id] if doc_id else None
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        if not self.is_available():
            return {'available': False}
        
        try:
            count = self.collection.count()
            return {
                'available': True,
                'document_count': count,
                'db_path': str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {'available': False}


# Global ChromaDB instance
_chroma_integration = None


@lru_cache(maxsize=1)
def get_chroma() -> ChromaIntegration:
    """Get global ChromaDB integration (lazy loaded)."""
    global _chroma_integration
    if _chroma_integration is None:
        from flask import current_app
        db_path = current_app.config.get('CHROMA_DB_PATH', 'data/chroma_db')
        _chroma_integration = ChromaIntegration(db_path)
    return _chroma_integration


def is_chroma_available() -> bool:
    """Check if ChromaDB is available."""
    try:
        return get_chroma().is_available()
    except:
        return False


def search_documents(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Search documents using ChromaDB."""
    try:
        return get_chroma().search_documents(query, n_results)
    except:
        return []


def get_chroma_info() -> Dict[str, Any]:
    """Get ChromaDB information."""
    try:
        return get_chroma().get_collection_info()
    except:
        return {'available': False}
