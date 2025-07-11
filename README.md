# FastAPI Vibe Coding - ChatGPT Chat with RAG

A modern FastAPI application featuring a beautiful chat interface with ChatGPT integration and Retrieval-Augmented Generation (RAG) capabilities using OpenAI embeddings.

## Features

- 🚀 **FastAPI Backend** - Modern, fast Python web framework
- 💬 **ChatGPT Integration** - Real AI-powered conversations
- 🔍 **RAG (Retrieval-Augmented Generation)** - Enhanced responses with knowledge base
- 🧠 **OpenAI Embeddings** - Semantic search using OpenAI's text-embedding-ada-002
- 🎨 **Beautiful Chat Interface** - Modern, responsive UI
- 📚 **Document Management** - Add and search through your knowledge base
- 🔧 **Simple Setup** - Easy installation and configuration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. Run the Application

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application

- **Chat Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints

- `GET /` - Serve the chat interface
- `GET /hello` - Simple hello world endpoint
- `GET /health` - Health check endpoint

### Chat & RAG Endpoints

- `POST /ask` - Send a message and get AI response with RAG
- `POST /add-document` - Add a document to the knowledge base
- `GET /vector-stats` - Get vector database statistics

### Example Usage

#### Add a Document to Knowledge Base

```bash
curl -X POST "http://localhost:8000/add-document" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints.",
       "metadata": "{\"source\": \"documentation\", \"topic\": \"web frameworks\"}"
     }'
```

#### Ask a Question

```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is FastAPI?"
     }'
```

#### Get Vector Database Stats

```bash
curl "http://localhost:8000/vector-stats"
```

## How RAG Works

1. **Document Storage**: Documents are converted to semantic embeddings using OpenAI's text-embedding-ada-002 model
2. **Semantic Search**: When you ask a question, the system finds the most semantically similar documents
3. **Enhanced Response**: ChatGPT receives both your question and relevant context
4. **Better Answers**: Responses are more accurate and contextual

## Project Structure

```
fastapi-vibe-coding/
├── main.py              # FastAPI application
├── vector_db.py         # OpenAI embeddings vector database
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from env.example)
├── env.example          # Environment variables template
├── static/
│   └── index.html       # Chat interface
└── README.md           # This file
```

## Dependencies

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **OpenAI** - ChatGPT API and embeddings integration
- **NumPy** - Numerical computing
- **python-dotenv** - Environment variable management

## Troubleshooting

### OpenAI API Key Issues

If you see fallback responses instead of ChatGPT responses:
1. Check that your `.env` file exists and contains `OPENAI_API_KEY`
2. Verify your API key is valid and has credits
3. Check the console for any error messages

### Installation Issues

If you encounter installation problems:
1. Make sure you're using Python 3.8 or higher
2. Try installing packages individually: `pip install fastapi uvicorn openai python-dotenv numpy`
3. Use a virtual environment: `python -m venv venv && source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

### Vector Database Issues

The vector database uses OpenAI embeddings for semantic search. If you encounter issues:
1. Check that your OpenAI API key is valid and has embedding credits
2. Verify the `vector_db.json` file is writable
3. Restart the application if needed

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
