from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import json
from vector_db import vector_db

# Load environment variables
load_dotenv()

# Initialize OpenAI client with error handling
openai_client = None
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print("✅ OpenAI client initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize OpenAI client: {e}")
    print("   The app will run in fallback mode with simple responses.")
    openai_client = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sources: list = []


class DocumentRequest(BaseModel):
    content: str
    metadata: str = "{}"


class DocumentResponse(BaseModel):
    success: bool
    message: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up FastAPI application...")
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("   Please set your OpenAI API key in a .env file or environment variable.")
        print("   The chat will fall back to simple responses.")
    else:
        print("✅ OpenAI API key found. ChatGPT integration enabled.")
    
    print("✅ Vector database initialized. RAG functionality enabled.")
    
    yield
    # Shutdown
    print("Shutting down FastAPI application...")


app = FastAPI(
    title="ChatGPT Chat API with RAG",
    description="A FastAPI application with ChatGPT integration, RAG functionality, and beautiful chat interface",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root() -> FileResponse:
    """Serve the chat interface."""
    return FileResponse("static/index.html")


@app.get("/hello")
async def hello_world() -> dict[str, str]:
    """Return a simple hello world message."""
    return {"message": "Hello, World!"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/vector-stats")
async def get_vector_stats() -> dict:
    """Get vector database statistics."""
    try:
        stats = vector_db.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vector stats: {str(e)}")


@app.post("/add-document", response_model=DocumentResponse)
async def add_document(request: DocumentRequest) -> DocumentResponse:
    """Add a document to the vector database for RAG."""
    try:
        metadata = {}
        if request.metadata:
            try:
                metadata = json.loads(request.metadata)
            except json.JSONDecodeError:
                metadata = {"raw_metadata": request.metadata}
        
        success = vector_db.add_document(request.content, metadata)
        if success:
            return DocumentResponse(success=True, message="Document added successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to add document")
    except Exception as e:
        import traceback
        print(f"Failed to add document: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return a response using ChatGPT with RAG."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        sources = []
        # Try to use ChatGPT API with RAG
        if openai.api_key:
            response, sources = await get_chatgpt_response_with_rag(request.message, return_sources=True)
        else:
            # Fallback to simple responses if no API key
            response = generate_fallback_response(request.message.lower())
        return ChatResponse(response=response, sources=sources)
    except Exception as e:
        print(f"Error in chat processing: {e}")
        # Fallback to simple response on error
        fallback_response = generate_fallback_response(request.message.lower())
        return ChatResponse(response=fallback_response, sources=[])


async def get_chatgpt_response_with_rag(message: str, return_sources: bool = False):
    """Get a response from ChatGPT API with RAG context and optionally return sources."""
    if not openai.api_key:
        return generate_fallback_response(message.lower()), [] if return_sources else generate_fallback_response(message.lower())
    try:
        # Get relevant context from vector database
        context = ""
        similar_docs = vector_db.search(message, top_k=3)
        sources = []
        if similar_docs:
            context_parts = []
            for result in similar_docs:
                context_parts.append(f"Relevant information: {result['document']['content']}")
                sources.append({
                    "content": result['document']['content'],
                    "metadata": result['document']['metadata'],
                    "score": result['score']
                })
            context = "\n\n".join(context_parts)
            context = f"\n\nContext from knowledge base:\n{context}\n\n"
        # Prepare system message with RAG context
        system_message = """You are a helpful, friendly AI assistant with access to a knowledge base. \
        Use the provided context to give accurate and helpful responses. \
        If the context is relevant to the user's question, incorporate it into your response.\
        If the context is not relevant or no context is provided, respond based on your general knowledge.\
        Keep your responses concise, helpful, and engaging."""
        # Prepare messages for ChatGPT
        messages = [
            {
                "role": "system",
                "content": system_message
            }
        ]
        # Add context if available
        if context:
            messages.append({
                "role": "user",
                "content": f"Here is some relevant context for the upcoming question:\n{context}"
            })
        # Add the actual user question
        messages.append({
            "role": "user",
            "content": message
        })
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        if return_sources:
            return response.choices[0].message.content.strip(), sources
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        if return_sources:
            return generate_fallback_response(message.lower()), []
        return generate_fallback_response(message.lower())


async def get_chatgpt_response(message: str) -> str:
    """Get a response from ChatGPT API (without RAG)."""
    if not openai.api_key:
        return generate_fallback_response(message.lower())
    
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful, friendly AI assistant. Keep your responses concise, helpful, and engaging. If you're asked about topics you can't help with (like real-time data), politely explain the limitation and suggest alternatives."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return generate_fallback_response(message.lower())


def generate_fallback_response(message: str) -> str:
    """Generate a fallback response when ChatGPT API is not available."""
    import random
    
    # Simple keyword-based responses
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    questions = ["how are you", "what's up", "how's it going"]
    thanks = ["thank you", "thanks", "thx"]
    weather = ["weather", "temperature", "forecast"]
    time = ["time", "clock", "hour"]
    
    if any(greeting in message for greeting in greetings):
        responses = [
            "Hello! How can I help you today?",
            "Hi there! Nice to meet you!",
            "Hey! I'm here to assist you.",
            "Greetings! What can I do for you?"
        ]
        return random.choice(responses)
    
    elif any(q in message for q in questions):
        responses = [
            "I'm doing great, thanks for asking! How about you?",
            "I'm functioning perfectly! Ready to help with anything you need.",
            "All systems operational! What can I assist you with today?"
        ]
        return random.choice(responses)
    
    elif any(t in message for t in thanks):
        responses = [
            "You're welcome! Is there anything else I can help you with?",
            "My pleasure! Let me know if you need anything else.",
            "Glad I could help! Feel free to ask more questions."
        ]
        return random.choice(responses)
    
    elif any(w in message for w in weather):
        return "I can't check the weather in real-time, but I'd recommend checking a weather app or website for the most accurate forecast!"
    
    elif any(t in message for t in time):
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    elif "help" in message:
        return "I can help you with general questions, greetings, and basic information. Just ask me anything!"
    
    elif "bye" in message or "goodbye" in message:
        responses = [
            "Goodbye! Have a great day!",
            "See you later! Feel free to come back anytime.",
            "Take care! I'll be here when you need me."
        ]
        return random.choice(responses)
    
    else:
        responses = [
            "That's interesting! Tell me more about that.",
            "I'm not sure I understand. Could you rephrase that?",
            "Interesting question! I'm still learning, but I'd love to help where I can.",
            "I'm here to help! Could you provide more context?",
            "That's a great point! What specifically would you like to know?"
        ]
        return random.choice(responses)


@app.get("/status")
async def status():
    """Return Milvus/OpenAI/collection status for UI display."""
    stats = vector_db.get_stats()
    openai_status = bool(openai.api_key)
    return {
        "milvus": stats,
        "openai": openai_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
