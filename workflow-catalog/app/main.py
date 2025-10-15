"""
Workflow Catalog Service - FastAPI Application
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import json

from .models import HealthCheck, DifficultyLevel
from .database import Database
from .services.parser import WorkflowParser
from .services.ingestion import WorkflowIngestion

# Initialize FastAPI app
app = FastAPI(
    title="Workflow Catalog Service",
    description="API for discovering and managing n8n workflows",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database()
parser = WorkflowParser()
ingestion = WorkflowIngestion()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await db.init_db()
    print("✅ Database initialized")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "service": "Workflow Catalog Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    workflow_count = await db.get_workflow_count()
    
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        database="connected",
        workflows_count=workflow_count,
        timestamp=datetime.utcnow()
    )


@app.get("/api/categories", tags=["Categories"])
async def list_categories():
    """List all workflow categories"""
    categories_data = await db.get_categories()
    
    categories = []
    for cat_dict in categories_data:
        categories.append({
            "name": cat_dict['category'],
            "slug": cat_dict['category'].lower().replace(' & ', '-').replace(' ', '-'),
            "workflow_count": cat_dict['workflow_count']
        })
    
    return categories


@app.get("/api/workflows/search", tags=["Workflows"])
async def search_workflows(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = None,
    difficulty: Optional[DifficultyLevel] = None,
    local_ai_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Search workflows with full-text search"""
    offset = (page - 1) * page_size
    
    workflows = await db.search_workflows(
        query=q,
        category=category,
        difficulty=difficulty.value if difficulty else None,
        local_ai_only=local_ai_only,
        limit=page_size,
        offset=offset
    )
    
    # Parse JSON fields
    for wf in workflows:
        wf['tags'] = json.loads(wf.get('tags', '[]'))
        wf['use_cases'] = json.loads(wf.get('use_cases', '[]'))
        wf['integrations'] = json.loads(wf.get('integrations', '[]'))
        wf['node_types'] = json.loads(wf.get('node_types', '[]'))
        wf['services'] = json.loads(wf.get('services', '[]'))
        wf['external_apis'] = json.loads(wf.get('external_apis', '[]'))
        wf['credentials'] = json.loads(wf.get('credentials', '[]'))
    
    return {
        "workflows": workflows,
        "total": len(workflows),
        "page": page,
        "page_size": page_size
    }


@app.get("/api/workflows/popular", tags=["Workflows"])
async def get_popular_workflows(
    limit: int = Query(10, ge=1, le=50)
):
    """Get most popular workflows"""
    workflows = await db.search_workflows(limit=limit, offset=0)
    
    # Parse JSON fields
    for wf in workflows:
        wf['tags'] = json.loads(wf.get('tags', '[]'))
        wf['use_cases'] = json.loads(wf.get('use_cases', '[]'))
        wf['integrations'] = json.loads(wf.get('integrations', '[]'))
        wf['node_types'] = json.loads(wf.get('node_types', '[]'))
        wf['services'] = json.loads(wf.get('services', '[]'))
        wf['external_apis'] = json.loads(wf.get('external_apis', '[]'))
        wf['credentials'] = json.loads(wf.get('credentials', '[]'))
    
    return {
        "workflows": workflows,
        "total": len(workflows),
        "page": 1,
        "page_size": limit
    }


@app.get("/api/workflows/compatible", tags=["Workflows"])
async def get_compatible_workflows(
    limit: int = Query(20, ge=1, le=100)
):
    """Get workflows compatible with local AI stack"""
    workflows = await db.search_workflows(
        local_ai_only=True,
        limit=limit,
        offset=0
    )
    
    # Parse JSON fields
    for wf in workflows:
        wf['tags'] = json.loads(wf.get('tags', '[]'))
        wf['use_cases'] = json.loads(wf.get('use_cases', '[]'))
        wf['integrations'] = json.loads(wf.get('integrations', '[]'))
        wf['node_types'] = json.loads(wf.get('node_types', '[]'))
        wf['services'] = json.loads(wf.get('services', '[]'))
        wf['external_apis'] = json.loads(wf.get('external_apis', '[]'))
        wf['credentials'] = json.loads(wf.get('credentials', '[]'))
    
    return {
        "workflows": workflows,
        "total": len(workflows),
        "page": 1,
        "page_size": limit
    }


@app.get("/api/workflows", tags=["Workflows"])
async def list_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    difficulty: Optional[DifficultyLevel] = None,
    local_ai_only: bool = False,
    tags: Optional[str] = None
):
    """List workflows with pagination and filters"""
    offset = (page - 1) * page_size
    tag_list = tags.split(',') if tags else []
    
    workflows = await db.search_workflows(
        category=category,
        difficulty=difficulty.value if difficulty else None,
        local_ai_only=local_ai_only,
        tags=tag_list,
        limit=page_size,
        offset=offset
    )
    
    # Parse JSON fields for each workflow
    for wf in workflows:
        wf['tags'] = json.loads(wf.get('tags', '[]'))
        wf['use_cases'] = json.loads(wf.get('use_cases', '[]'))
        wf['integrations'] = json.loads(wf.get('integrations', '[]'))
        wf['node_types'] = json.loads(wf.get('node_types', '[]'))
        wf['services'] = json.loads(wf.get('services', '[]'))
        wf['external_apis'] = json.loads(wf.get('external_apis', '[]'))
        wf['credentials'] = json.loads(wf.get('credentials', '[]'))
    
    total = await db.get_workflow_count()
    
    return {
        "workflows": workflows,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@app.get("/api/workflows/{workflow_id}", tags=["Workflows"])
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID"""
    wf_dict = await db.get_workflow(workflow_id)
    
    if not wf_dict:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Parse JSON fields
    wf_dict['tags'] = json.loads(wf_dict.get('tags', '[]'))
    wf_dict['use_cases'] = json.loads(wf_dict.get('use_cases', '[]'))
    wf_dict['integrations'] = json.loads(wf_dict.get('integrations', '[]'))
    wf_dict['node_types'] = json.loads(wf_dict.get('node_types', '[]'))
    wf_dict['services'] = json.loads(wf_dict.get('services', '[]'))
    wf_dict['external_apis'] = json.loads(wf_dict.get('external_apis', '[]'))
    wf_dict['credentials'] = json.loads(wf_dict.get('credentials', '[]'))
    
    return wf_dict


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
