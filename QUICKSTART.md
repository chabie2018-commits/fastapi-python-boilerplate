# FastAPI + RayMine Quick Start Guide

## 🚀 Setup Instructions

### 1. Clone and Setup
```bash
git clone https://github.com/chabie2018-commits/fastapi-python-boilerplate
cd fastapi-python-boilerplate
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
OPENAI_API_KEY=sk-proj-your-actual-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-actual-anon-key
```

### 4. Setup Supabase Database
- Follow instructions in `SUPABASE_SETUP.md`
- Create the `memories` table
- Ensure RLS policies are configured

### 5. Run Application
```bash
# Option A: Direct run
python main.py

# Option B: Uvicorn
uvicorn main:app --reload

# Option C: Docker
docker-compose up
```

Visit: `http://localhost:8000`

---

## 📡 API Usage Examples

### Cognition Endpoint
```bash
curl -X POST http://localhost:8000/api/cognition/think \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "retrieve_context": true
  }'
```

### Store Memory
```bash
curl -X POST http://localhost:8000/api/memory/store \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Machine learning is a subset of AI",
    "category": "knowledge",
    "metadata": {"source": "training"}
  }'
```

### Search Memory
```bash
curl -X POST http://localhost:8000/api/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "limit": 5
  }'
```

---

## 🔗 Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Ray Core**: https://github.com/chabie2018-commits/Ray
- **Supabase Docs**: https://supabase.com/docs

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Supabase Connection Error
- Check SUPABASE_URL and SUPABASE_KEY in `.env`
- Ensure memories table exists
- Verify network connectivity

### Issue: OpenAI API Error
- Check OPENAI_API_KEY is valid
- Verify API key is not expired
- Check account balance

---

## 📦 Project Structure
```
fastapi-python-boilerplate/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── raymine_client.py      # RayMine cognition engine
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Docker Compose setup
├── .env.example          # Environment template
├── SUPABASE_SETUP.md     # Database setup guide
└── README.md             # Documentation
```

---

## 🎯 Next Steps

1. ✅ Setup environment and dependencies
2. ✅ Configure Supabase database
3. ✅ Test API endpoints with curl or Postman
4. ✅ Integrate with your application
5. ✅ Deploy to production

---

**Ready to go!** 🚀
