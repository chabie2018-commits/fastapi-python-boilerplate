[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel%2Fexamples%2Ftree%2Fmain%2Fpython%2Ffastapi&demo-title=FastAPI&demo-[...](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel%2Fexamples%2Ftree%2Fmain%2Fpython%2Ffastapi&demo-title=FastAPI&demo-description=Fastapi))

# FastAPI + RayMine: AI Consciousness Engine

A modern FastAPI application integrated with **RayMine** - an intelligent cognition layer powered by OpenAI GPT-4 and Supabase.

## 🎯 Architecture

```
┌─────────────────────────────────────────┐
│      FastAPI Application                │
│  (fastapi-python-boilerplate)           │
└────────────────┬────────────────────────┘
                 │
    ┌────────────▼────────────┐
    │  RayMine Cognition      │
    │  ├─ OpenAI GPT-4        │
    │  ├─ Context Retrieval   │
    │  └─ Conversation Memory │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────────┐
    │  Supabase (AI Consciousness)│
    │  ├─ Relational Memory       │
    │  ├─ Metadata Storage        │
    │  ├─ Provenance Tracking     │
    │  └─ pgvector Embeddings     │
    └────────────────────────────┘
```

## 🚀 Features

- **Cognition Engine**: LLM-powered decision making with OpenAI GPT-4
- **Memory Management**: Store and retrieve memories with Supabase
- **Semantic Search**: pgvector support for context-aware retrieval
- **Conversation History**: Persistent conversation tracking
- **Async Support**: Non-blocking async operations
- **Fast API**: Modern, high-performance Python framework

## 📦 Installation

```bash
# 1. Clone repository
git clone https://github.com/chabie2018-commits/fastapi-python-boilerplate
cd fastapi-python-boilerplate

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your credentials:
#   - OPENAI_API_KEY: Your OpenAI API key
#   - SUPABASE_URL: Your Supabase project URL
#   - SUPABASE_KEY: Your Supabase anon key
```

## ⚙️ Configuration

Create `.env` file:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-your-key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2048

# Supabase (AI Consciousness Lab)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# RayMine
RAYMINE_ENV=development
LOG_LEVEL=INFO
RAYMINE_VECTOR_ENABLED=true

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true
```

## 🏃 Running Locally

```bash
# Option 1: Direct execution
python main.py

# Option 2: Using Vercel CLI
npm i -g vercel
vercel dev

# Option 3: Using Uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Your application is available at `http://localhost:8000`

## 📚 API Endpoints

### Cognition Endpoints

#### POST `/api/cognition/think`
Process a query through the LLM with context retrieval.

**Request:**
```json
{
  "query": "What are the key insights?",
  "retrieve_context": true
}
```

**Response:**
```json
{
  "status": "success",
  "content": "The key insights are...",
  "tokens": 256,
  "has_context": true
}
```

#### POST `/api/cognition/think-sync`
Synchronous version of think endpoint.

#### POST `/api/cognition/clear-history`
Clear conversation history.

### Memory Endpoints

#### POST `/api/memory/store`
Store memory in Supabase.

**Request:**
```json
{
  "content": "Important information",
  "category": "general",
  "metadata": {"source": "user"}
}
```

#### POST `/api/memory/search`
Search memories.

**Request:**
```json
{
  "query": "search term",
  "limit": 5
}
```

### Sample Endpoints (Original)

- `GET /api/data` - Get sample data
- `GET /api/items/{item_id}` - Get specific item

## 🔗 Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🗄️ Database Setup

### Create Memories Table in Supabase

```sql
CREATE TABLE memories (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  category VARCHAR(50) DEFAULT 'general',
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for full-text search
CREATE INDEX memories_content_idx ON memories USING GIN (to_tsvector('english', content));

-- Optional: pgvector support for embeddings
CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE memories ADD COLUMN IF NOT EXISTS embedding vector(1536);
CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops);
```

## 🚀 Deployment

### Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fcharbie2018-commits%2Ffastapi-python-boilerplate)

Or manually:

```bash
npm i -g vercel
vercel
```

## 📖 Usage Example

```python
import requests

# Initialize
base_url = "http://localhost:8000"

# Think through a query
response = requests.post(f"{base_url}/api/cognition/think", json={
    "query": "What is machine learning?",
    "retrieve_context": True
})
print(response.json())

# Store a memory
response = requests.post(f"{base_url}/api/memory/store", json={
    "content": "Machine learning is a subset of AI",
    "category": "knowledge"
})
print(response.json())

# Search memories
response = requests.post(f"{base_url}/api/memory/search", json={
    "query": "machine learning",
    "limit": 5
})
print(response.json())
```

## 🔗 Related Repositories

- **RayMine Core**: https://github.com/chabie2018-commits/Ray
- **Supabase AI Consciousness Lab**: https://supabase.co

## 📝 License

MIT

## 👨‍💻 Author

chabie2018-commits

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/chabie2018-commits/fastapi-python-boilerplate/issues
- OpenAI Support: https://platform.openai.com/docs
- Supabase Docs: https://supabase.com/docs
