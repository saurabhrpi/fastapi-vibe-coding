from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


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
    yield
    # Shutdown
    print("Shutting down FastAPI application...")


app = FastAPI(
    title="ChatGPT Chat API",
    description="A FastAPI application with ChatGPT integration and beautiful chat interface",
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


@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return a response using ChatGPT."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Try to use ChatGPT API
        if os.getenv("OPENAI_API_KEY"):
            response = await get_chatgpt_response(request.message)
        else:
            # Fallback to simple responses if no API key
            response = generate_fallback_response(request.message.lower())
        
        return ChatResponse(response=response)
        
    except Exception as e:
        print(f"Error in chat processing: {e}")
        # Fallback to simple response on error
        fallback_response = generate_fallback_response(request.message.lower())
        return ChatResponse(response=fallback_response)


async def get_chatgpt_response(message: str) -> str:
    """Get a response from ChatGPT API."""
    try:
        response = openai_client.chat.completions.create(
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
        raise e


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
