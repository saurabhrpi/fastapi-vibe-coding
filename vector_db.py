import numpy as np
import json
import os
from typing import List, Dict, Optional
from pymilvus import MilvusClient
import openai
import logging
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

HOST = "in03-874be76b9aa0be7.serverless.gcp-us-west1.cloud.zilliz.com"  # No https://
TOKEN = "268c3796886a41827afcee6560f083fbfc4992ae7265598b4d3582979748054380929293cd76ea79244845abf9773e4e9128de0e"  # Replace with your actual token

class MilvusVectorDB:
    def __init__(
        self,
        collection_name: str = "firstRAGExample",
        embedding_model: str = "text-embedding-3-large",
        dimension: int = 3072,
        host: str = HOST,
        token: str = TOKEN
    ):
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.dimension = dimension
        self.host = host
        self.token = token
        self.collection = None
        self.milvus_client = None
        self._connect_to_milvus()
        self._init_collection()

    def _connect_to_milvus(self):
        """Connect to Zilliz Cloud using MilvusClient and token-based authentication"""
        try:
            self.milvus_client = MilvusClient(
                uri=f"https://{self.host}",
                token=self.token
            )
            logger.info(f"✅ Connected to Zilliz Cloud at https://{self.host} using MilvusClient")
        except Exception as e:
            logger.error(f"Failed to connect to Zilliz Cloud: {e}")
            logger.info("⚠️  Zilliz Cloud not available. Using local fallback mode.")
            self.milvus_client = None

    def _init_collection(self):
        """Initialize the Milvus collection using MilvusClient methods"""
        if not self.milvus_client:
            self.collection = None
            return
        try:
            if not self.milvus_client.has_collection(self.collection_name):
                schema = {
                    "fields": [
                        {"name": "primary_key", "description": "PK", "type": "INT64", "is_primary": True, "autoID": True},
                        {"name": "content", "description": "Content", "type": "VARCHAR", "max_length": 65535},
                        {"name": "metadata", "description": "Metadata", "type": "VARCHAR", "max_length": 65535},
                        {"name": "embedding", "description": "Embedding vector", "type": "FLOAT_VECTOR", "dim": self.dimension}
                    ],
                    "description": "Chat documents collection"
                }
                self.milvus_client.create_collection(self.collection_name, schema=schema)
                logger.info(f"✅ Created Milvus collection: {self.collection_name}")
                # Create index
                index_params = {
                    "field_name": "embedding",
                    "index_type": "IVF_FLAT",
                    "metric_type": "COSINE",
                    "params": {"nlist": 128}
                }
                self.milvus_client.create_index(self.collection_name, index_params)
            else:
                logger.info(f"✅ Loaded existing Milvus collection: {self.collection_name}")
            self.collection = self.collection_name
        except Exception as e:
            logger.error(f"Failed to create/load collection: {e}")
            self.collection = None

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text using OpenAI API"""
        try:
            response = openai.Embedding.create(
                input=text,
                model=self.embedding_model
            )
            embedding = response['data'][0]['embedding']
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            logger.error(f"Error getting embedding from OpenAI: {e}")
            return np.zeros(self.dimension)

    def add_document(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Add a document to the Milvus collection using MilvusClient"""
        if not self.collection or not self.milvus_client:
            logger.warning("Milvus collection not available")
            return False
        try:
            embedding = self._get_embedding(content)
            metadata_str = json.dumps(metadata or {})
            # Generate a unique primary key (e.g., using current timestamp in ms)
            primary_key = int(time.time() * 1000)
            data = {
                "primary_key": primary_key,
                "content": [content],
                "metadata": [metadata_str],
                "embedding": [embedding.tolist()]
            }
            self.milvus_client.insert(self.collection, data)
            logger.info(f"✅ Added document to Milvus (embedding dim: {len(embedding)})")
            return True
        except Exception as e:
            logger.error(f"Error adding document to Milvus: {e}")
            return False

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar documents in Milvus using MilvusClient"""
        if not self.collection or not self.milvus_client:
            logger.warning("Milvus collection not available")
            return []
        try:
            query_embedding = self._get_embedding(query)
            search_params = {
                "data": [query_embedding.tolist()],
                "anns_field": "embedding",
                "param": {"metric_type": "COSINE", "params": {"nprobe": 10}},
                "limit": top_k,
                "output_fields": ["content", "metadata"]
            }
            results = self.milvus_client.search(self.collection, search_params)
            formatted_results = []
            for hit in results[0]:
                try:
                    metadata = json.loads(hit.get("metadata", "{}"))
                except:
                    metadata = {}
                formatted_results.append({
                    'document': {
                        'id': hit.get("primary_key", None),
                        'content': hit.get("content", ""),
                        'metadata': metadata
                    },
                    'score': float(hit.get("score", 0))
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching Milvus: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get Milvus collection statistics using MilvusClient"""
        if not self.collection or not self.milvus_client:
            return {
                'status': 'not_connected',
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.dimension
            }
        try:
            stats = self.milvus_client.get_collection_stats(self.collection)
            return {
                'status': 'connected',
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.dimension,
                'total_entities': stats.get('row_count', 0),
                'milvus_host': f"{self.host}"
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'status': 'error',
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.dimension,
                'error': str(e)
            }

    def clear_db(self) -> bool:
        """Clear all documents from the collection using MilvusClient"""
        if not self.collection or not self.milvus_client:
            return False
        try:
            self.milvus_client.drop_collection(self.collection)
            logger.info(f"✅ Dropped Milvus collection: {self.collection}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

# Global instance
vector_db = MilvusVectorDB() 