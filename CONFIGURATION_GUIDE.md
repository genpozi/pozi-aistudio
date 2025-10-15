# Pozi AI Studio - Configuration Guide

## ✅ Services Status

All services are running and healthy! Ollama models are downloaded and ready.

**Available Models:**
- `qwen2.5:7b-instruct-q4_K_M` (4.7 GB) - Chat/Completion
- `nomic-embed-text` (274 MB) - Embeddings

## 🔗 Access Your Services

### Step 1: Find Your Gitpod URLs

In your Gitpod workspace, look for the **PORTS** tab (usually at the bottom). You should see these ports:

| Port | Service | Status |
|------|---------|--------|
| 80 | Caddy (Main Proxy) | Should be public |
| 8001 | n8n | Make public |
| 8002 | Open WebUI | Make public |
| 8003 | Flowise | Make public |
| 8005 | Supabase Studio | Make public |
| 8007 | Langfuse | Make public |
| 8008 | Neo4j Browser | Make public |

**Make ports public**: Right-click each port → Change Visibility → Public

Your URLs will look like:
- n8n: `https://8001-[your-workspace-url].gitpod.io`
- Open WebUI: `https://8002-[your-workspace-url].gitpod.io`
- etc.

## 📝 Step-by-Step Configuration

### 1️⃣ Configure n8n (Port 8001)

#### A. Create Admin Account
1. Open n8n URL from Gitpod ports
2. Fill in:
   - **Email**: Your email
   - **First Name**: Your name
   - **Last Name**: Your last name
   - **Password**: Choose a secure password
3. Click "Get Started"

#### B. Configure Credentials

Go to **Settings** → **Credentials** → **Add Credential**

##### Ollama Credential
- **Type**: Search "Ollama"
- **Name**: `Local Ollama`
- **Base URL**: `http://ollama:11434`
- Click **Save**

##### PostgreSQL Credential (Supabase)
- **Type**: Search "Postgres"
- **Name**: `Supabase Database`
- **Host**: `db`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: `a3f7e9d2c5b8a1f4e7d9c2b5a8f1e4d7c9b2a5f8e1d4c7b9a2e5f8d1c4b7a9e2`
- **Port**: `5432`
- **SSL**: Disabled
- Click **Save**

##### Qdrant Credential
- **Type**: Search "Qdrant"
- **Name**: `Local Qdrant`
- **URL**: `http://qdrant:6333`
- **API Key**: `any-key-works-locally` (not validated locally)
- Click **Save**

##### OpenRouter Credential (Free Models)
- **Type**: Search "OpenAI" (OpenRouter is OpenAI-compatible)
- **Name**: `OpenRouter Free Models`
- **API Key**: `[Your OpenRouter API Key from .env]`
- **Base URL**: `https://openrouter.ai/api/v1`
- Click **Save**

**Free Models to Use:**
- `meta-llama/llama-4-maverick:free`
- `openai/gpt-oss-20b:free`
- `z-ai/glm-4.5-air:free`
- `deepseek/deepseek-chat-v3.1:free`
- `meta-llama/llama-3.3-70b-instruct:free`

##### Perplexity Credential
- **Type**: Search "OpenAI" (Perplexity is OpenAI-compatible)
- **Name**: `Perplexity`
- **API Key**: `[Your Perplexity API Key from .env]`
- **Base URL**: `https://api.perplexity.ai`
- Click **Save**

##### Google Gemini Credential
- **Type**: Search "Google Gemini"
- **Name**: `Google Gemini`
- **API Key**: `[Your Gemini API Key from .env]`
- Click **Save**

##### Brave Search Credential
- **Type**: Search "HTTP Request" (for custom API)
- **Name**: `Brave Search`
- **Authentication**: Generic Credential Type
- **Generic Auth Type**: Header Auth
- **Credential Data**:
  - **Name**: `X-Subscription-Token`
  - **Value**: `[Your Brave API Key from .env]`
- Click **Save**

##### Replicate Credential
- **Type**: Search "Replicate"
- **Name**: `Replicate`
- **API Token**: `[Your Replicate API Key from .env]`
- Click **Save**

#### C. Test Pre-loaded Workflows

You have 3 RAG workflows already imported:
1. **V1 Local RAG AI Agent** - Basic RAG with local models
2. **V2 Local Supabase RAG AI Agent** - RAG with Supabase storage
3. **V3 Local Agentic RAG AI Agent** - Advanced agentic RAG

**To test a workflow:**
1. Go to **Workflows**
2. Open "V3 Local Agentic RAG AI Agent"
3. Click on credential nodes and select the credentials you just created
4. Click **Execute Workflow** to test

### 2️⃣ Configure Open WebUI (Port 8002)

#### A. Create Admin Account
1. Open Open WebUI URL from Gitpod ports
2. Click "Sign Up"
3. Fill in:
   - **Name**: Your name
   - **Email**: Your email
   - **Password**: Choose a secure password
4. Click "Create Account"

#### B. Add n8n Integration

1. Go to **Workspace** → **Functions**
2. Click **"+"** to add a new function
3. **Name**: `n8n Agent`
4. **Description**: `Connect to n8n workflows`
5. **Code**: Copy from `n8n_pipe.py` file in the project root
6. Click **Save**

#### C. Configure n8n Webhook

1. In n8n, open a workflow with a webhook trigger
2. Copy the **Production Webhook URL**
3. Back in Open WebUI, click the gear icon on your n8n function
4. Set `n8n_url` to your webhook URL
5. Toggle the function **ON**

Now you can select "n8n Agent" from the model dropdown in Open WebUI!

### 3️⃣ Configure Supabase (Port 8005)

1. Open Supabase Studio URL
2. **Login**:
   - Username: `supabase`
   - Password: `PoziAIStudio2025SecurePassword`
3. Explore your database, create tables, manage auth

**Database Connection String:**
```
postgresql://postgres:a3f7e9d2c5b8a1f4e7d9c2b5a8f1e4d7c9b2a5f8e1d4c7b9a2e5f8d1c4b7a9e2@db:5432/postgres
```

### 4️⃣ Configure Neo4j (Port 8008)

1. Open Neo4j Browser URL
2. **Connect**:
   - Connect URL: `bolt://localhost:7687`
   - Username: `neo4j`
   - Password: `PoziNeo4jSecurePass2025`
3. Run your first query: `MATCH (n) RETURN n LIMIT 25`

### 5️⃣ Configure Langfuse (Port 8007)

1. Open Langfuse URL
2. Create your account (first user becomes admin)
3. Create a project
4. Get your API keys from Settings
5. Use these keys in your n8n workflows for observability

### 6️⃣ Configure Flowise (Port 8003)

1. Open Flowise URL
2. Start building AI agents with drag-and-drop
3. Connect to Ollama: `http://ollama:11434`
4. Connect to Qdrant: `http://qdrant:6333`

## 🧪 Testing Your Setup

### Test Ollama
```bash
docker exec ollama ollama run qwen2.5:7b-instruct-q4_K_M "Hello, how are you?"
```

### Test Qdrant
```bash
curl http://localhost:6333/collections
```

### Test n8n API
```bash
curl http://localhost:8001/healthz
```

## 🔧 Useful Commands

### View all running services
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Check n8n logs
```bash
docker logs n8n -f
```

### Check Ollama logs
```bash
docker logs ollama -f
```

### Restart a service
```bash
docker compose -p localai restart n8n
```

### Access Ollama CLI
```bash
docker exec -it ollama ollama list
docker exec -it ollama ollama run qwen2.5:7b-instruct-q4_K_M
```

## 📊 Monitoring

### Check service health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep healthy
```

### Check resource usage
```bash
docker stats --no-stream
```

## 🎯 Next Steps

1. ✅ Configure all credentials in n8n
2. ✅ Test the pre-loaded RAG workflows
3. ✅ Set up Open WebUI and connect to n8n
4. ✅ Upload documents to test RAG functionality
5. ✅ Explore Flowise for visual agent building
6. ✅ Use Langfuse to monitor your LLM calls

## 🆘 Troubleshooting

### Can't access services?
- Check Gitpod ports tab
- Make sure ports are set to "Public"
- Try refreshing the page

### Credentials not working in n8n?
- Double-check the connection strings
- Ensure service names match (e.g., `db` not `localhost`)
- Test connection in n8n credential editor

### Ollama not responding?
```bash
docker logs ollama
docker exec ollama ollama list
```

### Database connection failed?
- Verify password matches `.env` file
- Use `db` as hostname (not `localhost`)
- Port should be `5432`

## 📚 Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Open WebUI Docs](https://docs.openwebui.com/)
- [Ollama Models](https://ollama.com/library)
- [Supabase Docs](https://supabase.com/docs)
- [Qdrant Docs](https://qdrant.tech/documentation/)

---

**Environment Ready!** Start with n8n and work your way through each service. 🚀
