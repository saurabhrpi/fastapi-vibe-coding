"""
Sample documents for RAG functionality.
You can use these examples to populate your vector database.
"""

SAMPLE_DOCUMENTS = [
    {
        "content": "FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints. It was created by Sebastián Ramírez and is designed to be easy to use and highly performant. FastAPI is built on top of Starlette and Pydantic, providing automatic API documentation, data validation, and serialization.",
        "metadata": '{"category": "technology", "topic": "fastapi", "source": "documentation"}'
    },
    {
        "content": "Retrieval-Augmented Generation (RAG) is a technique that combines the power of large language models with external knowledge retrieval. It works by first retrieving relevant documents or information from a knowledge base, then using that context to generate more accurate and informed responses. This approach helps reduce hallucinations and provides more factual answers.",
        "metadata": '{"category": "ai", "topic": "rag", "source": "research"}'
    },
    {
        "content": "Milvus is an open-source vector database designed for AI applications. It provides high-performance similarity search and analytics for unstructured data. Milvus supports various distance metrics and index types, making it ideal for applications like recommendation systems, image search, and natural language processing tasks.",
        "metadata": '{"category": "technology", "topic": "vector_database", "source": "documentation"}'
    },
    {
        "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming. It has a large standard library and extensive ecosystem of third-party packages.",
        "metadata": '{"category": "programming", "topic": "python", "source": "documentation"}'
    },
    {
        "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed. It uses algorithms and statistical models to analyze and draw inferences from patterns in data. Common applications include image recognition, natural language processing, recommendation systems, and predictive analytics.",
        "metadata": '{"category": "ai", "topic": "machine_learning", "source": "educational"}'
    },
    {
        "content": "Docker is a platform for developing, shipping, and running applications in containers. Containers are lightweight, portable, and self-sufficient units that can run anywhere Docker is installed. Docker provides isolation, consistency, and efficiency for application deployment and development workflows.",
        "metadata": '{"category": "technology", "topic": "docker", "source": "documentation"}'
    },
    {
        "content": "REST (Representational State Transfer) is an architectural style for designing networked applications. It uses HTTP methods (GET, POST, PUT, DELETE) to perform operations on resources. REST APIs are stateless, cacheable, and follow a client-server architecture. They are widely used for web services and mobile applications.",
        "metadata": '{"category": "web", "topic": "rest_api", "source": "educational"}'
    },
    {
        "content": "Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret, and manipulate human language. It combines computational linguistics with machine learning and deep learning. Applications include chatbots, sentiment analysis, language translation, and text summarization.",
        "metadata": '{"category": "ai", "topic": "nlp", "source": "educational"}'
    }
]


def add_sample_documents(vector_db):
    """Add sample documents to the vector database."""
    try:
        vector_db.add_documents(SAMPLE_DOCUMENTS)
        print(f"✅ Added {len(SAMPLE_DOCUMENTS)} sample documents to the vector database")
        print("You can now ask questions about FastAPI, RAG, Milvus, Python, and more!")
    except Exception as e:
        print(f"❌ Failed to add sample documents: {e}")


if __name__ == "__main__":
    # This can be run directly to populate the database
    from vector_db import get_vector_db
    
    vector_db = get_vector_db()
    if vector_db:
        add_sample_documents(vector_db)
    else:
        print("❌ Vector database not available. Please ensure Milvus is running.") 