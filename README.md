## FastAPI Hello World API

A simple FastAPI application with a hello world endpoint.

### Features

- Hello World endpoint (`/`)
- Health check endpoint (`/health`)
- Interactive API documentation
- Proper startup/shutdown handling

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

#### Option 1: Using Python directly
```bash
python main.py
```

#### Option 2: Using Uvicorn directly
```bash
uvicorn main:app --reload
```

The `--reload` flag enables auto-reload during development.

### API Endpoints

- **GET /** - Hello World message
  - Returns: `{"message": "Hello, World!"}`
  
- **GET /health** - Health check
  - Returns: `{"status": "healthy"}`

### Accessing the API

- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc

### Development

The server runs on port 8000 by default. You can change this by modifying the `uvicorn.run()` call in `main.py` or by using the `--port` flag with uvicorn.
