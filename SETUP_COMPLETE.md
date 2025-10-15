# Pozi AI Studio - Setup Complete! ✅

## Services Status

All services are now running! Here's what's available:

### Core Services

| Service | Internal Port | Caddy Port | Status |
|---------|--------------|------------|--------|
| **n8n** (Workflow Automation) | 5678 | 8001 | ✅ Running |
| **Open WebUI** (Chat Interface) | 8080 | 8002 | ✅ Running |
| **Flowise** (AI Agent Builder) | 3001 | 8003 | ✅ Running |
| **Supabase Studio** (Database) | 8000 | 8005 | ✅ Running |
| **Langfuse** (LLM Observability) | 3000 | 8007 | ✅ Running |
| **Neo4j** (Graph Database) | 7474 | 8008 | ✅ Running |
| **Ollama** (Local LLMs) | 11434 | - | ✅ Running (downloading models) |
| **Qdrant** (Vector Store) | 6333 | - | ✅ Running |
| **SearXNG** (Search Engine) | 8080 | 8006 | ✅ Running |

### Access URLs (Gitpod Environment)

Since you're in Gitpod, you'll need to access services through port forwarding. The main ports are:

- **Port 80/443**: Caddy reverse proxy (main entry point)
- **Port 8001**: n8n
- **Port 8002**: Open WebUI
- **Port 8003**: Flowise
- **Port 8005**: Supabase
- **Port 8007**: Langfuse
- **Port 8008**: Neo4j

Gitpod should automatically detect these ports and provide URLs. Check the "Ports" tab in your Gitpod workspace.

## Initial Setup Steps

### 1. n8n (Workflow Automation)
- Access via port 8001
- **First time setup**: Create your admin account
- **Pre-loaded workflows**: 3 RAG AI Agent workflows are already imported
- **Configure credentials**:
  - Ollama: `http://ollama:11434`
  - Postgres (Supabase): Host: `db`, User: `postgres`, Password: from `.env`
  - Qdrant: `http://qdrant:6333`

### 2. Open WebUI (Chat Interface)
- Access via port 8002
- **First time setup**: Create your admin account
- **Add n8n integration**:
  1. Go to Workspace → Functions → Add Function
  2. Paste code from `n8n_pipe.py`
  3. Configure the n8n webhook URL from your workflow

### 3. Configure AI Provider Keys

Your API keys are stored in `.env` but need to be configured in the respective UIs:

#### In n8n (Credentials):
1. Go to Settings → Credentials
2. Add new credentials for each provider:

**OpenRouter** (Free Models):
- API Key: `[Your OpenRouter API Key from .env]`
- Base URL: `https://openrouter.ai/api/v1`
- Free models to use:
  - `meta-llama/llama-4-maverick:free`
  - `openai/gpt-oss-20b:free`
  - `z-ai/glm-4.5-air:free`
  - `deepseek/deepseek-chat-v3.1:free`
  - `meta-llama/llama-3.3-70b-instruct:free`

**Perplexity** (Best Models):
- API Key: `[Your Perplexity API Key from .env]`

**Gemini** (Best Models):
- API Key: `[Your Gemini API Key from .env]`

**Brave Search**:
- API Key: `[Your Brave API Key from .env]`

**Replicate**:
- API Key: `[Your Replicate API Key from .env]`

#### In Open WebUI (Admin Settings):
1. Go to Admin Panel → Settings → Connections
2. Add external API providers as needed

### 4. Supabase Setup
- Access via port 8005
- **Login**: 
  - Username: `supabase`
  - Password: `PoziAIStudio2025SecurePassword`
- **Database connection** (for n8n):
  - Host: `db`
  - Port: `5432`
  - Database: `postgres`
  - User: `postgres`
  - Password: Check `.env` for `POSTGRES_PASSWORD`

### 5. Neo4j Setup
- Access via port 8008
- **Login**:
  - Username: `neo4j`
  - Password: `PoziNeo4jSecurePass2025`

## Ollama Models

Ollama is currently downloading these models:
- `qwen2.5:7b-instruct-q4_K_M` (for chat/completion)
- `nomic-embed-text` (for embeddings)

Check download progress:
```bash
docker logs ollama-pull-llama
```

## Important Notes

### ⚠️ GPU Configuration
- **Current Profile**: CPU (AMD GPU not available in Gitpod)
- Ollama is running in CPU mode with low VRAM settings
- For production with AMD GPU, you'll need a machine with `/dev/kfd` and `/dev/dri` devices

### 🔒 Security
- All secrets have been generated with secure random values
- **Change these in production**:
  - Supabase dashboard password
  - Neo4j password
  - All JWT secrets and encryption keys

### 📝 Environment Variables
Your API keys are stored in `.env`:
- `OPENROUTER_API_KEY`
- `PERPLEXITY_API_KEY`
- `GEMINI_API_KEY`
- `BRAVE_API_KEY`
- `REPLICATE_API_KEY`

## Next Steps

1. **Access n8n** (port 8001) and create your admin account
2. **Explore the pre-loaded workflows**:
   - V1 Local RAG AI Agent
   - V2 Local Supabase RAG AI Agent
   - V3 Local Agentic RAG AI Agent
3. **Configure your AI provider credentials** in n8n
4. **Set up Open WebUI** (port 8002) and integrate with n8n
5. **Test the RAG workflows** with your documents

## Useful Commands

### Check service status:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### View logs:
```bash
docker logs n8n
docker logs ollama
docker logs open-webui
```

### Restart services:
```bash
docker compose -p localai restart n8n
```

### Stop all services:
```bash
docker compose -p localai down
```

### Start services again:
```bash
python3 start_services.py --profile cpu --environment public
```

## Troubleshooting

### Ollama models not downloading?
```bash
docker logs ollama-pull-llama -f
```

### n8n not accessible?
```bash
docker logs n8n
docker logs caddy
```

### Database connection issues?
Check that the Postgres password in your n8n credentials matches the one in `.env`

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Ollama Documentation](https://ollama.com/docs)
- [Original Project](https://github.com/coleam00/local-ai-packaged)

---

**Setup completed at**: 2025-10-15 17:39 UTC
**Profile**: CPU
**Environment**: Public
