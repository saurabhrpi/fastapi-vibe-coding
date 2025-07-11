# fastapi-vibe-coding
This repo is to learn how to vibe code with Cursor

## FastAPI ChatGPT Chat Application

A beautiful FastAPI application with an interactive chat interface powered by ChatGPT.

### Features

- **🤖 Real ChatGPT Integration**: Powered by OpenAI's GPT-3.5-turbo model
- **🎨 Beautiful UI**: Modern, responsive chat interface with animations
- **⚡ Fast API**: FastAPI backend with async processing
- **🛡️ Fallback System**: Works even without API key (simple responses)
- **📱 Mobile Friendly**: Responsive design for all devices
- **🔧 Easy Setup**: Simple configuration and deployment

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API Key** (Optional but recommended):
   
   **Option A: Using .env file**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_actual_api_key_here
   ```
   
   **Option B: Environment variable**
   ```bash
   # Windows
   set OPENAI_API_KEY=your_actual_api_key_here
   
   # Linux/Mac
   export OPENAI_API_KEY=your_actual_api_key_here
   ```
   
   **Get an API key:**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key to your `.env` file or environment variable

3. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or with auto-reload:
   ```bash
   uvicorn main:app --reload
   ```

4. **Open your browser:**
   - Go to `http://localhost:8000`
   - Start chatting with ChatGPT!

### API Endpoints

- **GET /** - Beautiful chat interface (HTML page)
- **GET /hello** - Hello World message
- **GET /health** - Health check endpoint
- **POST /ask** - Chat API endpoint with ChatGPT integration
  - Request: `{"message": "your message here"}`
  - Returns: `{"response": "AI response"}`

### Chat Features

The chat interface includes:
- **Real-time messaging** with loading animations
- **User/AI message distinction** with avatars
- **Error handling** with graceful fallbacks
- **Keyboard shortcuts** (Enter to send)
- **Auto-scroll** to latest messages
- **Mobile-responsive** design

### Configuration

Customize the ChatGPT integration:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | `gpt-3.5-turbo` |

### Development

- **Port**: 8000 (configurable)
- **Auto-reload**: Use `uvicorn main:app --reload`
- **API Docs**: Available at `/docs` and `/redoc`

### How It Works

1. **Frontend**: Beautiful HTML/CSS/JS chat interface
2. **Backend**: FastAPI server with `/ask` endpoint
3. **ChatGPT**: OpenAI API integration with fallback responses
4. **Static Files**: Served from `/static` directory

### Troubleshooting

- **No API Key**: App will use fallback responses
- **API Errors**: Graceful fallback to simple responses
- **Port Issues**: Change port in `main.py` or use `--port` flag

### File Structure

```
fastapi-vibe-coding/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── env.example         # Environment template
├── static/
│   └── index.html      # Chat interface
└── README.md           # This file
```

**Note**: If you don't set up an OpenAI API key, the chat will still work using intelligent fallback responses, but you won't get the full ChatGPT experience.
