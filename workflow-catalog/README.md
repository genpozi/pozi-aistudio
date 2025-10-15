# Workflow Catalog Service

A microservice for discovering, analyzing, and cataloging n8n workflows from GitHub repositories.

## Features

- **Workflow Discovery**: Automatically fetch workflows from GitHub repositories
- **Full-Text Search**: SQLite FTS5 for fast workflow search
- **Compatibility Analysis**: Detect workflows compatible with local AI stack (Ollama, Qdrant, etc.)
- **Smart Categorization**: Automatic categorization into 15+ categories
- **Difficulty Assessment**: Beginner, Intermediate, Advanced levels
- **REST API**: FastAPI-based API for workflow discovery

## Architecture

```
workflow-catalog/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # SQLite with FTS5
│   └── services/
│       ├── parser.py        # Workflow JSON parser
│       └── ingestion.py     # GitHub ingestion pipeline
├── scripts/
│   └── ingest_workflows.py  # CLI ingestion script
├── data/
│   ├── workflows.db         # SQLite database
│   └── workflows/           # Downloaded workflow JSONs
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Ingest Workflows

```bash
python3 scripts/ingest_workflows.py
```

This will:
- Fetch workflows from configured GitHub repositories
- Parse and analyze each workflow
- Store metadata in SQLite database
- Generate ingestion summary

### 3. Start API Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /health
```
Returns service health status and workflow count.

### List Categories
```bash
GET /api/categories
```
Returns all workflow categories with counts.

### Search Workflows (Full-Text)
```bash
GET /api/workflows/search?q=chatbot&local_ai_only=true
```
Full-text search across workflow names, descriptions, tags, and use cases.

### Popular Workflows
```bash
GET /api/workflows/popular?limit=10
```
Returns most popular workflows sorted by popularity score.

### Compatible Workflows
```bash
GET /api/workflows/compatible?limit=20
```
Returns workflows compatible with local AI stack (Ollama, Qdrant, etc.).

### List Workflows
```bash
GET /api/workflows?page=1&page_size=20&category=AI%20%26%20Machine%20Learning
```

Query Parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `category`: Filter by category
- `difficulty`: Filter by difficulty (beginner/intermediate/advanced)
- `local_ai_only`: Show only local AI compatible workflows (boolean)
- `tags`: Comma-separated tags

### Get Workflow by ID
```bash
GET /api/workflows/{workflow_id}
```
Returns detailed information for a specific workflow.

## Database Schema

The SQLite database includes:

- **workflows table**: 40+ fields including metadata, requirements, compatibility
- **workflows_fts**: FTS5 virtual table for full-text search
- **Automatic triggers**: Keep search index synchronized
- **Indexes**: Optimized for category, difficulty, compatibility queries

## Workflow Sources

Currently configured repositories:

1. **Zie619/n8n-workflows** (2,057 workflows)
   - Large community collection
   - Diverse use cases

2. **enescingoz/awesome-n8n-templates** (285 workflows)
   - Curated high-quality templates
   - Well-documented workflows

## Compatibility Analysis

The service analyzes workflows for compatibility with Pozi AI Studio's local services:

### Local Services Detected
- Ollama (local LLM)
- Postgres
- Qdrant (vector database)
- Supabase
- Neo4j
- Langfuse
- Redis
- MinIO
- ClickHouse

### Compatibility Scores
- **Fully Compatible** (1.0): Works entirely with local services
- **Partially Compatible** (0.5-0.9): Mix of local and external services
- **Requires External** (0.1-0.4): Primarily external APIs
- **Incompatible** (0.0): Cannot run locally

## Categories

Workflows are automatically categorized into:

- AI & Machine Learning
- Data & Analytics
- Business & Productivity
- Communication & Collaboration
- Content & Media
- Development & DevOps
- E-commerce & Sales
- Finance & Accounting
- HR & Recruitment
- Marketing & Social Media
- Security & Monitoring
- Support & Customer Service
- Utilities & Tools
- Integration & Automation
- Other

## Testing

Run the test script to verify database and API functionality:

```bash
python3 test_api.py
```

## Configuration

Edit `app/services/ingestion.py` to add more GitHub repositories:

```python
REPOS = {
    'owner/repo-name': {
        'workflows_path': 'path/to/workflows',
        'branch': 'main',
    },
}
```

## Performance

- **Ingestion**: ~50 workflows in 10-15 seconds
- **Search**: Sub-millisecond FTS5 queries
- **Database**: Lightweight SQLite, no external dependencies

## Future Enhancements

- [ ] Workflow import to n8n instance
- [ ] Credential configuration automation
- [ ] Workflow testing and validation
- [ ] Community ratings and reviews
- [ ] Workflow recommendations
- [ ] Version tracking and updates
- [ ] Export to different formats

## License

MIT
