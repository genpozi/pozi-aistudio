"""
Pydantic models for workflow catalog
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CompatibilityStatus(str, Enum):
    FULLY_COMPATIBLE = "fully_compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    REQUIRES_EXTERNAL = "requires_external"
    INCOMPATIBLE = "incompatible"


class WorkflowRequirements(BaseModel):
    credentials: List[str] = []
    services: List[str] = []
    external_apis: List[str] = []
    min_n8n_version: str = "1.0.0"


class WorkflowMetadata(BaseModel):
    node_count: int
    integrations: List[str] = []
    node_types: List[str] = []
    has_webhook: bool = False
    has_schedule: bool = False
    estimated_runtime: Optional[str] = None


class WorkflowCompatibility(BaseModel):
    local_ai: bool
    requires_external_api: bool
    works_offline: bool
    pozi_compatible: bool
    status: CompatibilityStatus
    compatibility_score: float = Field(ge=0.0, le=1.0)


class WorkflowStats(BaseModel):
    popularity_score: int = 0
    import_count: int = 0
    success_rate: float = 0.0
    avg_setup_time: Optional[str] = None


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    author: Optional[str] = None
    source_repo: str
    source_url: Optional[HttpUrl] = None
    tags: List[str] = []
    department: Optional[str] = None
    use_cases: List[str] = []


class WorkflowCreate(WorkflowBase):
    json_path: str
    metadata: WorkflowMetadata
    requirements: WorkflowRequirements
    compatibility: WorkflowCompatibility


class Workflow(WorkflowBase):
    id: str
    json_path: str
    metadata: WorkflowMetadata
    requirements: WorkflowRequirements
    compatibility: WorkflowCompatibility
    stats: WorkflowStats
    created_at: datetime
    updated_at: datetime
    last_synced: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowList(BaseModel):
    workflows: List[Workflow]
    total: int
    page: int
    page_size: int


class WorkflowSearchQuery(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    local_ai_only: bool = False
    tags: List[str] = []
    page: int = 1
    page_size: int = 20


class Category(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    workflow_count: int = 0
    subcategories: List[str] = []


class ImportRequest(BaseModel):
    workflow_id: str
    configure_credentials: bool = True


class ImportResponse(BaseModel):
    success: bool
    workflow_id: str
    n8n_workflow_id: Optional[str] = None
    message: str
    credentials_configured: List[str] = []
    credentials_needed: List[str] = []


class HealthCheck(BaseModel):
    status: str
    version: str
    database: str
    workflows_count: int
    timestamp: datetime
