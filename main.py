from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from config import settings
from raymine_client import get_raymine


# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Vercel + FastAPI + RayMine",
    description="FastAPI with RayMine AI Consciousness Engine",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ThinkRequest(BaseModel):
    """Request model for cognition endpoint"""
    query: str
    retrieve_context: bool = True


class ThinkResponse(BaseModel):
    """Response model for cognition endpoint"""
    status: str
    content: Optional[str] = None
    tokens: Optional[int] = None
    error: Optional[str] = None


class MemoryRequest(BaseModel):
    """Request model for memory endpoint"""
    content: str
    category: str = "general"
    metadata: Optional[Dict[str, Any]] = None


class MemorySearchRequest(BaseModel):
    """Request model for memory search"""
    query: str
    limit: int = 5


# Cognition Endpoints
@app.post("/api/cognition/think", response_model=ThinkResponse)
async def think(request: ThinkRequest) -> Dict[str, Any]:
    """Process a thought/query through RayMine cognition engine"""
    try:
        raymine = get_raymine()
        result = await raymine.think_async(request.query, request.retrieve_context)
        return result
    except Exception as e:
        logger.error(f"Error in think endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cognition/think-sync")
def think_sync(request: ThinkRequest) -> Dict[str, Any]:
    """Synchronous version of think endpoint"""
    try:
        raymine = get_raymine()
        result = raymine.think(request.query, request.retrieve_context)
        return result
    except Exception as e:
        logger.error(f"Error in think_sync endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cognition/clear-history")
def clear_history() -> Dict[str, str]:
    """Clear conversation history"""
    try:
        raymine = get_raymine()
        raymine.clear_history()
        return {"status": "success", "message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Memory Endpoints
@app.post("/api/memory/store")
def store_memory(request: MemoryRequest) -> Dict[str, Any]:
    """Store memory in Supabase"""
    try:
        raymine = get_raymine()
        result = raymine.memory.store(request.content, request.category, request.metadata)
        return result
    except Exception as e:
        logger.error(f"Error storing memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/search")
def search_memory(request: MemorySearchRequest) -> Dict[str, Any]:
    """Search memories"""
    try:
        raymine = get_raymine()
        result = raymine.memory.search(request.query, request.limit)
        return result
    except Exception as e:
        logger.error(f"Error searching memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Sample Endpoints (Original)
@app.get("/api/data")
def get_sample_data():
    return {
        "data": [
            {"id": 1, "name": "Sample Item 1", "value": 100},
            {"id": 2, "name": "Sample Item 2", "value": 200},
            {"id": 3, "name": "Sample Item 3", "value": 300}
        ],
        "total": 3,
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    return {
        "item": {
            "id": item_id,
            "name": "Sample Item " + str(item_id),
            "value": item_id * 100
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FastAPI + RayMine</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <script>
            window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
        </script>
        <script defer src="/_vercel/speed-insights/script.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                color: #ffffff;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            header {
                border-bottom: 1px solid #333333;
                padding: 0;
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(10px);
            }
            
            nav {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                padding: 1rem 2rem;
                gap: 2rem;
            }
            
            .logo {
                font-size: 1.5rem;
                font-weight: 700;
                background: linear-gradient(to right, #00d4ff, #0099ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-decoration: none;
            }
            
            .nav-links {
                display: flex;
                gap: 1.5rem;
                margin-left: auto;
            }
            
            .nav-links a {
                text-decoration: none;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.875rem;
                font-weight: 500;
            }
            
            .nav-links a:hover {
                color: #00d4ff;
                background-color: rgba(0, 212, 255, 0.1);
            }
            
            main {
                flex: 1;
                max-width: 1200px;
                margin: 0 auto;
                padding: 4rem 2rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            
            .hero {
                margin-bottom: 3rem;
            }
            
            h1 {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 1rem;
                background: linear-gradient(to right, #00d4ff, #0099ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.25rem;
                color: #888888;
                margin-bottom: 2rem;
                max-width: 600px;
            }
            
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: linear-gradient(to right, #00d4ff, #0099ff);
                color: #ffffff;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 2rem;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                background-color: #00ff88;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                width: 100%;
                max-width: 900px;
            }
            
            .card {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 255, 0.05) 100%);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
                transition: all 0.3s ease;
                text-align: left;
                backdrop-filter: blur(10px);
            }
            
            .card:hover {
                border-color: rgba(0, 212, 255, 0.5);
                transform: translateY(-4px);
                box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
            }
            
            .card h3 {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
                color: #00d4ff;
            }
            
            .card p {
                color: #aaaaaa;
                font-size: 0.9rem;
                margin-bottom: 1rem;
                line-height: 1.5;
            }
            
            .card a {
                display: inline-flex;
                align-items: center;
                color: #00d4ff;
                text-decoration: none;
                font-size: 0.875rem;
                font-weight: 600;
                padding: 0.75rem 1.5rem;
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 6px;
                transition: all 0.2s ease;
            }
            
            .card a:hover {
                background: rgba(0, 212, 255, 0.2);
                border-color: #00d4ff;
            }
            
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
                margin-top: 3rem;
                width: 100%;
                max-width: 900px;
            }
            
            .feature {
                padding: 1rem;
                background: rgba(0, 0, 0, 0.3);
                border-left: 3px solid #00d4ff;
                border-radius: 4px;
            }
            
            .feature-title {
                font-weight: 600;
                color: #00d4ff;
                margin-bottom: 0.5rem;
            }
            
            .feature-desc {
                font-size: 0.85rem;
                color: #888888;
            }
            
            @media (max-width: 768px) {
                nav {
                    padding: 1rem;
                    flex-direction: column;
                    gap: 1rem;
                }
                
                h1 {
                    font-size: 2rem;
                }
                
                .cards {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">🧠 RayMine</a>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                    <a href="/api/data">Sample Data</a>
                </div>
            </nav>
        </header>
        <main>
            <div class="hero">
                <div class="status-badge">
                    <span class="status-dot"></span>
                    AI Consciousness Engine Active
                </div>
                <h1>FastAPI + RayMine</h1>
                <p class="subtitle">
                    Intelligent cognition layer powered by OpenAI GPT-4 and Supabase
                </p>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h3>🧠 Cognition Engine</h3>
                    <p>Process queries through OpenAI GPT-4 with intelligent context retrieval from Supabase memory.</p>
                    <a href="/docs#/Cognition">View Endpoints →</a>
                </div>
                
                <div class="card">
                    <h3>💾 Memory System</h3>
                    <p>Store and retrieve memories using Supabase PostgreSQL with semantic search capabilities.</p>
                    <a href="/docs#/Memory">View Endpoints →</a>
                </div>
                
                <div class="card">
                    <h3>📊 Vector Embeddings</h3>
                    <p>pgvector support for semantic search and context-aware memory retrieval.</p>
                    <a href="/docs">Learn More →</a>
                </div>
            </div>
            
            <div class="feature-grid">
                <div class="feature">
                    <div class="feature-title">🚀 OpenAI Integration</div>
                    <div class="feature-desc">GPT-4 powered cognition and reasoning</div>
                </div>
                <div class="feature">
                    <div class="feature-title">🗄️ Supabase Backend</div>
                    <div class="feature-desc">PostgreSQL with real-time capabilities</div>
                </div>
                <div class="feature">
                    <div class="feature-title">🔄 Async Support</div>
                    <div class="feature-desc">Non-blocking async operations</div>
                </div>
                <div class="feature">
                    <div class="feature-title">📝 Conversation Memory</div>
                    <div class="feature-desc">Persistent conversation history</div>
                </div>
                <div class="feature">
                    <div class="feature-title">🔍 Semantic Search</div>
                    <div class="feature-desc">Context-aware memory retrieval</div>
                </div>
                <div class="feature">
                    <div class="feature-title">⚡ FastAPI</div>
                    <div class="feature-desc">Modern, fast Python framework</div>
                </div>
            </div>
        </main>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload,
    )
