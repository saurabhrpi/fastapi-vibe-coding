import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import openai
import logging
from dotenv import load_dotenv

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
        embedding_model: str = "text-embedding-ada-002",
        dimension: int = 1536,
        host: str = HOST,
        token: str = TOKEN
    ):
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.dimension = dimension
        self.host = host
        self.token = token
        self.collection = None
        # OpenAI embedding setup is above
        # Connect to Milvus
        self._connect_to_milvus()
        # Initialize collection
        self._init_collection()
    
    def _connect_to_milvus(self):
        """Connect to Zilliz Cloud using token-based authentication"""
        try:
            from pymilvus import connections
            connections.connect(
                alias="default",
                uri=f"https://{self.host}",
                token=self.token
            )
            logger.info(f"✅ Connected to Zilliz Cloud at https://{self.host}")
        except Exception as e:
            logger.error(f"Failed to connect to Zilliz Cloud: {e}")
            logger.info("⚠️  Zilliz Cloud not available. Using local fallback mode.")
            self.collection = None
    
    def _init_collection(self):
        """Initialize the Milvus collection"""
        if not utility.has_collection(self.collection_name):
            try:
                # Define collection schema
                fields = [
                    FieldSchema(name="primary_key", dtype=DataType.INT64, is_primary=True, auto_id=True),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
                ]
                schema = CollectionSchema(fields=fields, description="Chat documents collection")
                
                # Create collection
                self.collection = Collection(name=self.collection_name, schema=schema)
                
                # Create index
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
                self.collection.create_index(field_name="embedding", index_params=index_params)
                logger.info(f"✅ Created Milvus collection: {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to create collection: {e}")
                self.collection = None
        else:
            try:
                self.collection = Collection(self.collection_name)
                self.collection.load()
                logger.info(f"✅ Loaded existing Milvus collection: {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to load collection: {e}")
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
        """Add a document to the Milvus collection"""
        if not self.collection:
            logger.warning("Milvus collection not available")
            return False
        
        try:
            # Get embedding
            embedding = self._get_embedding(content)
            
            # Prepare metadata
            metadata_str = json.dumps(metadata or {})
            
            # Insert data
            data = [
                [content],
                [metadata_str],
                [embedding.tolist()]
            ]
            
            self.collection.insert(data)
            logger.info(f"✅ Added document to Milvus (embedding dim: {len(embedding)})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to Milvus: {e}")
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar documents in Milvus"""
        if not self.collection:
            logger.warning("Milvus collection not available")
            return []
        
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding.tolist()],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["content", "metadata"]
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    try:
                        metadata = json.loads(hit.entity.get("metadata", "{}"))
                    except:
                        metadata = {}
                    
                    formatted_results.append({
                        'document': {
                            'id': hit.id,
                            'content': hit.entity.get("content", ""),
                            'metadata': metadata
                        },
                        'score': float(hit.score)
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching Milvus: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get Milvus collection statistics"""
        if not self.collection:
            return {
                'status': 'not_connected',
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.dimension
            }
        
        try:
            stats = self.collection.get_statistics()
            return {
                'status': 'connected',
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.dimension,
                'total_entities': stats.get('row_count', 0),
                'milvus_host': f"{self.host}:{self.port}"
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
        """Clear all documents from the collection"""
        if not self.collection:
            return False
        
        try:
            utility.drop_collection(self.collection_name)
            logger.info(f"✅ Dropped Milvus collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

# Global instance
vector_db = MilvusVectorDB() 