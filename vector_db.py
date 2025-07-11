import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional
import openai
from sklearn.metrics.pairwise import cosine_similarity

class OpenAIVectorDB:
    def __init__(self, db_file: str = "vector_db.json", embedding_model: str = "text-embedding-ada-002"):
        self.db_file = db_file
        self.embedding_model = embedding_model
        self.documents = []
        self.embeddings = []
        self.load_db()
    
    def load_db(self):
        """Load existing documents from file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.embeddings = data.get('embeddings', [])
                    # Convert embeddings back to numpy arrays
                    self.embeddings = [np.array(emb) for emb in self.embeddings]
                print(f"✅ Loaded {len(self.documents)} documents with embeddings")
            except Exception as e:
                print(f"Error loading vector database: {e}")
                self.documents = []
                self.embeddings = []
    
    def save_db(self):
        """Save documents and embeddings to file"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            embeddings_list = [emb.tolist() for emb in self.embeddings]
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'documents': self.documents,
                    'embeddings': embeddings_list
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving vector database: {e}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text using OpenAI API"""
        try:
            response = openai.Embedding.create(
                input=text,
                model=self.embedding_model
            )
            return np.array(response['data'][0]['embedding'])
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(1536)  # OpenAI ada-002 embedding dimension
    
    def add_document(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Add a document to the vector database"""
        try:
            # Get embedding for the document
            embedding = self._get_embedding(content)
            
            doc = {
                'id': len(self.documents),
                'content': content,
                'metadata': metadata or {}
            }
            
            self.documents.append(doc)
            self.embeddings.append(embedding)
            self.save_db()
            
            print(f"✅ Added document with embedding (dimension: {len(embedding)})")
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar documents using semantic similarity"""
        if not self.documents or not self.embeddings:
            return []
        
        try:
            # Get embedding for the query
            query_embedding = self._get_embedding(query)
            
            # Calculate cosine similarities
            similarities = []
            for doc_embedding in self.embeddings:
                similarity = cosine_similarity(
                    [query_embedding], 
                    [doc_embedding]
                )[0][0]
                similarities.append(similarity)
            
            # Get top k results
            similarities = np.array(similarities)
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include relevant results
                    results.append({
                        'document': self.documents[idx],
                        'score': float(similarities[idx])
                    })
            
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        embedding_dim = len(self.embeddings[0]) if self.embeddings else 0
        return {
            'total_documents': len(self.documents),
            'embedding_model': self.embedding_model,
            'embedding_dimension': embedding_dim,
            'db_file': self.db_file,
            'has_embeddings': len(self.embeddings) > 0
        }
    
    def clear_db(self) -> bool:
        """Clear all documents and embeddings"""
        try:
            self.documents = []
            self.embeddings = []
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False

# Global instance
vector_db = OpenAIVectorDB() 