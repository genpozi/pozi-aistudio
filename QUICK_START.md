# 🚀 Pozi AI Studio - Quick Start

## ✅ Environment Status: READY!

Your complete AI development environment is running with **27 services**!

## 📍 You Are Here

```
✅ Docker containers running
✅ Ollama models downloaded (qwen2.5:7b-instruct, nomic-embed-text)
✅ All services healthy
✅ API keys configured in .env
✅ 3 RAG workflows pre-loaded in n8n
```

## 🎯 Next: Access Your Services

### Step 1: Find Your URLs

Look at the **PORTS** tab in your Gitpod workspace (bottom panel). You'll see:

| Port | Service | What It Does |
|------|---------|--------------|
| 8001 | **n8n** | Build AI workflows & agents |
| 8002 | **Open WebUI** | ChatGPT-like interface |
| 8003 | **Flowise** | Visual AI agent builder |
| 8005 | **Supabase** | Database & auth |
| 8007 | **Langfuse** | Monitor LLM usage |
| 8008 | **Neo4j** | Graph database |

**Important**: Right-click each port → **Change Visibility** → **Public**

Your URLs will look like:
```
https://8001-[workspace-id].gitpod.io  ← n8n
https://8002-[workspace-id].gitpod.io  ← Open WebUI
```

### Step 2: Configure n8n (5 minutes)

1. **Open n8n** (port 8001)
2. **Create your account** (first user = admin)
3. **Add credentials** (Settings → Credentials):

#### Quick Credential Setup

**Ollama** (Local AI):
- Type: `Ollama`
- Base URL: `http://ollama:11434`

**Supabase Database**:
- Type: `Postgres`
- Host: `db`
- Database: `postgres`
- User: `postgres`
- Password: `a3f7e9d2c5b8a1f4e7d9c2b5a8f1e4d7c9b2a5f8e1d4c7b9a2e5f8d1c4b7a9e2`
- Port: `5432`

**Qdrant** (Vector DB):
- Type: `Qdrant`
- URL: `http://qdrant:6333`
- API Key: `any-key` (not validated locally)

**OpenRouter** (Free Cloud Models):
- Type: `OpenAI`
- API Key: `[Your OpenRouter API Key from .env]`
- Base URL: `https://openrouter.ai/api/v1`

**Perplexity**:
- Type: `OpenAI`
- API Key: `[Your Perplexity API Key from .env]`
- Base URL: `https://api.perplexity.ai`

**Google Gemini**:
- Type: `Google Gemini`
- API Key: `[Your Gemini API Key from .env]`

### Step 3: Test a Workflow (2 minutes)

1. In n8n, go to **Workflows**
2. Open **"V3 Local Agentic RAG AI Agent"**
3. Click on nodes with credential icons
4. Select the credentials you just created
5. Click **Execute Workflow**

### Step 4: Set Up Open WebUI (3 minutes)

1. **Open Open WebUI** (port 8002)
2. **Create your account**
3. **Add n8n integration**:
   - Workspace → Functions → Add Function
   - Copy code from `n8n_pipe.py`
   - Configure with your n8n webhook URL

## 🎓 What You Can Do Now

### 1. Chat with Local AI
- Use Open WebUI with Ollama models
- No API costs, fully private

### 2. Build RAG Systems
- Upload documents to n8n workflows
- Create knowledge bases with Qdrant
- Query with natural language

### 3. Use Cloud AI (Free Models)
- OpenRouter free models (no credit card needed)
- Perplexity for web-enhanced responses
- Gemini for Google's latest models

### 4. Build Complex Agents
- Use n8n's visual workflow builder
- Combine multiple AI models
- Add tools, memory, and logic

### 5. Monitor Everything
- Langfuse tracks all LLM calls
- See costs, latency, and quality
- Debug and optimize

## 📚 Documentation Files

- **CONFIGURATION_GUIDE.md** - Detailed setup for each service
- **SETUP_COMPLETE.md** - Full service reference
- **n8n_credentials_template.json** - All credentials in one place
- **verify_setup.sh** - Check system health
- **test_ollama.sh** - Test local AI

## 🧪 Quick Tests

### Test Ollama
```bash
./test_ollama.sh
```

### Verify Everything
```bash
./verify_setup.sh
```

### Check Service Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### View Logs
```bash
docker logs n8n -f
docker logs ollama -f
```

## 🆘 Common Issues

### Can't access services?
- Check Gitpod PORTS tab
- Set ports to "Public" visibility
- Refresh the page

### Credentials not working?
- Use service names (e.g., `db` not `localhost`)
- Double-check passwords from `.env`
- Test connection in n8n

### Ollama slow?
- Running on CPU (no GPU in Gitpod)
- Use smaller models or cloud APIs for speed

## 🎯 Recommended First Project

**Build a Document Q&A System:**

1. Open n8n workflow "V3 Local Agentic RAG AI Agent"
2. Configure all credentials
3. Upload a PDF document
4. Ask questions about it
5. See RAG in action!

## 💡 Pro Tips

1. **Use OpenRouter free models** for testing (no costs)
2. **Combine local + cloud**: Ollama for embeddings, cloud for chat
3. **Monitor with Langfuse**: Track what works best
4. **Start simple**: Test one workflow before building complex agents
5. **Check logs**: `docker logs [service-name]` solves most issues

## 🔗 Quick Links

- [n8n Docs](https://docs.n8n.io/)
- [Ollama Models](https://ollama.com/library)
- [OpenRouter Free Models](https://openrouter.ai/models?free=true)
- [Supabase Docs](https://supabase.com/docs)

## 🎉 You're All Set!

Your environment is ready. Start with n8n (port 8001) and explore!

**Questions?** Check the detailed guides:
- `CONFIGURATION_GUIDE.md` - Step-by-step setup
- `SETUP_COMPLETE.md` - Complete reference

---

**Built with**: n8n • Ollama • Supabase • Open WebUI • Qdrant • Neo4j • Langfuse • Flowise
