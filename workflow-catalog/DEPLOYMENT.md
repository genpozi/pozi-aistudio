# Workflow Catalog Service - Deployment Guide

## Current Deployment

The Workflow Catalog Service is currently running in the Gitpod environment:

**API URL**: [https://8765--0199e8c2-147a-7a3e-90b2-135472412e6f.us-east-1-01.gitpod.dev](https://8765--0199e8c2-147a-7a3e-90b2-135472412e6f.us-east-1-01.gitpod.dev)

**n8n URL**: [https://5678--0199e8c2-147a-7a3e-90b2-135472412e6f.us-east-1-01.gitpod.dev](https://5678--0199e8c2-147a-7a3e-90b2-135472412e6f.us-east-1-01.gitpod.dev)

## Quick Start

### 1. Install Dependencies

```bash
cd workflow-catalog
pip install -r requirements.txt
```

### 2. Ingest Workflows (Optional - already done)

```bash
python3 scripts/ingest_workflows.py
```

This will:
- Fetch workflows from GitHub repositories
- Parse and analyze each workflow
- Store in SQLite database
- Generate summary statistics

### 3. Start API Server

```bash
# Development
uvicorn app.main:app --host 0.0.0.0 --port 8765 --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8765 --workers 4
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:8765/health

# List categories
curl http://localhost:8765/api/categories

# Get workflows
curl "http://localhost:8765/api/workflows?page=1&page_size=10"
```

## API Endpoints

### Health & Status
- `GET /` - Service info
- `GET /health` - Health check with workflow count

### Workflows
- `GET /api/workflows` - List workflows (paginated, filterable)
- `GET /api/workflows/{id}` - Get specific workflow
- `GET /api/workflows/search?q=query` - Full-text search
- `GET /api/workflows/popular?limit=10` - Popular workflows
- `GET /api/workflows/compatible?limit=20` - Local AI compatible

### Categories
- `GET /api/categories` - List all categories with counts

## Query Parameters

### List Workflows (`/api/workflows`)
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `category` (string): Filter by category
- `difficulty` (enum): beginner, intermediate, advanced
- `local_ai_only` (bool): Show only local AI compatible
- `tags` (string): Comma-separated tags

### Search (`/api/workflows/search`)
- `q` (string): Search query (searches name, description, tags, use cases)
- `category` (string): Filter by category
- `difficulty` (enum): beginner, intermediate, advanced
- `local_ai_only` (bool): Show only local AI compatible
- `page` (int): Page number
- `page_size` (int): Items per page

## Example Requests

### Get Local AI Compatible Workflows
```bash
curl "http://localhost:8765/api/workflows/compatible?limit=5" | jq .
```

### Search for Chatbot Workflows
```bash
curl "http://localhost:8765/api/workflows/search?q=chatbot&local_ai_only=true" | jq .
```

### Filter by Category and Difficulty
```bash
curl "http://localhost:8765/api/workflows?category=AI%20%26%20Machine%20Learning&difficulty=beginner&page_size=10" | jq .
```

### Get Specific Workflow
```bash
curl "http://localhost:8765/api/workflows/0ee1965d-660b-473a-8cd8-f85335952b87" | jq .
```

## Database

The service uses SQLite with FTS5 for full-text search:

- **Location**: `data/workflows.db`
- **Size**: ~300KB (97 workflows)
- **Tables**: 
  - `workflows` - Main workflow data (40+ fields)
  - `workflows_fts` - FTS5 virtual table for search
- **Indexes**: category, difficulty, compatibility, popularity

### Database Schema

Key fields:
- Basic: id, name, description, category, difficulty
- Metadata: node_count, integrations, node_types
- Requirements: credentials, services, external_apis
- Compatibility: local_ai, compatibility_score, status
- Stats: popularity_score, import_count, success_rate

## Performance

- **Ingestion**: ~50 workflows in 10-15 seconds
- **Search**: Sub-millisecond FTS5 queries
- **API Response**: <100ms for most endpoints
- **Database**: Lightweight, no external dependencies

## Monitoring

### Health Check
```bash
curl http://localhost:8765/health
```

Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "workflows_count": 97,
  "timestamp": "2025-10-15T23:51:30.123456"
}
```

### Logs
```bash
# View API logs
tail -f /tmp/workflow-api.log

# Check for errors
grep ERROR /tmp/workflow-api.log
```

## Troubleshooting

### Port Already in Use
```bash
# Kill existing process
lsof -ti:8765 | xargs kill -9

# Or use different port
uvicorn app.main:app --host 0.0.0.0 --port 8766
```

### Database Locked
```bash
# Stop all API instances
pkill -f "uvicorn app.main:app"

# Restart
uvicorn app.main:app --host 0.0.0.0 --port 8765
```

### Import Errors
```bash
# Ensure you're in the correct directory
cd workflow-catalog

# Check Python path
python3 -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Production Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/ ./data/

EXPOSE 8765

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765", "--workers", "4"]
```

Build and run:
```bash
docker build -t workflow-catalog .
docker run -d -p 8765:8765 -v $(pwd)/data:/app/data workflow-catalog
```

### Systemd Service

Create `/etc/systemd/system/workflow-catalog.service`:

```ini
[Unit]
Description=Workflow Catalog Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/workflow-catalog
Environment="PATH=/opt/workflow-catalog/venv/bin"
ExecStart=/opt/workflow-catalog/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8765 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable workflow-catalog
sudo systemctl start workflow-catalog
sudo systemctl status workflow-catalog
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name workflows.yourdomain.com;

    location / {
        proxy_pass http://localhost:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

1. **CORS**: Currently allows all origins (`*`). Update in production:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Rate Limiting**: Add rate limiting middleware for production

3. **Authentication**: Consider adding API key authentication for write operations

4. **Database**: Ensure proper file permissions on `data/workflows.db`

## Maintenance

### Update Workflows
```bash
# Re-run ingestion to fetch latest workflows
python3 scripts/ingest_workflows.py
```

### Backup Database
```bash
# Backup
cp data/workflows.db data/workflows.db.backup

# Restore
cp data/workflows.db.backup data/workflows.db
```

### Validate System
```bash
# Run validation suite
python3 scripts/validate_phase1.py
```

## Next Steps (Phase 2)

1. **Workflow Import**: Implement n8n API integration
2. **Credential Management**: Automate credential configuration
3. **Testing Framework**: Add workflow validation
4. **UI Development**: Build React-based browser
5. **Recommendations**: ML-based workflow suggestions
6. **Version Tracking**: Monitor workflow updates
7. **Community Features**: Ratings and reviews

## Support

For issues or questions:
- Check logs: `/tmp/workflow-api.log`
- Run validation: `python3 scripts/validate_phase1.py`
- Review documentation: `README.md` and `PHASE1_COMPLETE.md`

## License

MIT
