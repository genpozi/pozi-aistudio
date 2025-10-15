"""
SQLite database with FTS5 full-text search
"""
import aiosqlite
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "data/workflows.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self):
        """Initialize database with schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Main workflows table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    difficulty TEXT NOT NULL,
                    author TEXT,
                    source_repo TEXT NOT NULL,
                    source_url TEXT,
                    json_path TEXT NOT NULL,
                    tags TEXT,
                    department TEXT,
                    use_cases TEXT,
                    
                    -- Metadata
                    node_count INTEGER,
                    integrations TEXT,
                    node_types TEXT,
                    has_webhook INTEGER DEFAULT 0,
                    has_schedule INTEGER DEFAULT 0,
                    estimated_runtime TEXT,
                    
                    -- Requirements
                    credentials TEXT,
                    services TEXT,
                    external_apis TEXT,
                    min_n8n_version TEXT,
                    
                    -- Compatibility
                    local_ai INTEGER DEFAULT 0,
                    requires_external_api INTEGER DEFAULT 0,
                    works_offline INTEGER DEFAULT 1,
                    pozi_compatible INTEGER DEFAULT 0,
                    compatibility_status TEXT,
                    compatibility_score REAL,
                    
                    -- Stats
                    popularity_score INTEGER DEFAULT 0,
                    import_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    avg_setup_time TEXT,
                    
                    -- Timestamps
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_synced TEXT
                )
            """)
            
            # FTS5 virtual table for full-text search
            await db.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS workflows_fts USING fts5(
                    name,
                    description,
                    tags,
                    use_cases,
                    integrations,
                    content=workflows,
                    content_rowid=rowid
                )
            """)
            
            # Triggers to keep FTS in sync
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS workflows_ai AFTER INSERT ON workflows BEGIN
                    INSERT INTO workflows_fts(rowid, name, description, tags, use_cases, integrations)
                    VALUES (new.rowid, new.name, new.description, new.tags, new.use_cases, new.integrations);
                END
            """)
            
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS workflows_ad AFTER DELETE ON workflows BEGIN
                    DELETE FROM workflows_fts WHERE rowid = old.rowid;
                END
            """)
            
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS workflows_au AFTER UPDATE ON workflows BEGIN
                    UPDATE workflows_fts SET 
                        name = new.name,
                        description = new.description,
                        tags = new.tags,
                        use_cases = new.use_cases,
                        integrations = new.integrations
                    WHERE rowid = new.rowid;
                END
            """)
            
            # Categories table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE,
                    description TEXT,
                    workflow_count INTEGER DEFAULT 0
                )
            """)
            
            # Indexes
            await db.execute("CREATE INDEX IF NOT EXISTS idx_category ON workflows(category)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_difficulty ON workflows(difficulty)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_local_ai ON workflows(local_ai)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_compatibility ON workflows(compatibility_status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_popularity ON workflows(popularity_score DESC)")
            
            await db.commit()
    
    async def insert_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Insert a workflow into the database"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO workflows (
                        id, name, description, category, subcategory, difficulty,
                        author, source_repo, source_url, json_path, tags, department,
                        use_cases, node_count, integrations, node_types, has_webhook,
                        has_schedule, estimated_runtime, credentials, services,
                        external_apis, min_n8n_version, local_ai, requires_external_api,
                        works_offline, pozi_compatible, compatibility_status,
                        compatibility_score, popularity_score, import_count,
                        success_rate, avg_setup_time, created_at, updated_at, last_synced
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (
                    workflow['id'],
                    workflow['name'],
                    workflow.get('description'),
                    workflow['category'],
                    workflow.get('subcategory'),
                    workflow['difficulty'],
                    workflow.get('author'),
                    workflow['source_repo'],
                    workflow.get('source_url'),
                    workflow['json_path'],
                    json.dumps(workflow.get('tags', [])),
                    workflow.get('department'),
                    json.dumps(workflow.get('use_cases', [])),
                    workflow['metadata']['node_count'],
                    json.dumps(workflow['metadata'].get('integrations', [])),
                    json.dumps(workflow['metadata'].get('node_types', [])),
                    1 if workflow['metadata'].get('has_webhook') else 0,
                    1 if workflow['metadata'].get('has_schedule') else 0,
                    workflow['metadata'].get('estimated_runtime'),
                    json.dumps(workflow['requirements'].get('credentials', [])),
                    json.dumps(workflow['requirements'].get('services', [])),
                    json.dumps(workflow['requirements'].get('external_apis', [])),
                    workflow['requirements'].get('min_n8n_version', '1.0.0'),
                    1 if workflow['compatibility']['local_ai'] else 0,
                    1 if workflow['compatibility']['requires_external_api'] else 0,
                    1 if workflow['compatibility']['works_offline'] else 0,
                    1 if workflow['compatibility']['pozi_compatible'] else 0,
                    workflow['compatibility']['status'],
                    workflow['compatibility']['compatibility_score'],
                    workflow['stats'].get('popularity_score', 0),
                    workflow['stats'].get('import_count', 0),
                    workflow['stats'].get('success_rate', 0.0),
                    workflow['stats'].get('avg_setup_time'),
                    workflow['created_at'],
                    workflow['updated_at'],
                    workflow.get('last_synced')
                ))
                await db.commit()
                return True
            except Exception as e:
                print(f"Error inserting workflow: {e}")
                return False
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a workflow by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM workflows WHERE id = ?", (workflow_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
    
    async def search_workflows(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        local_ai_only: bool = False,
        tags: List[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search workflows with filters"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            conditions = []
            params = []
            
            if query:
                # Use FTS5 for full-text search
                conditions.append("""
                    rowid IN (
                        SELECT rowid FROM workflows_fts 
                        WHERE workflows_fts MATCH ?
                    )
                """)
                params.append(query)
            
            if category:
                conditions.append("category = ?")
                params.append(category)
            
            if difficulty:
                conditions.append("difficulty = ?")
                params.append(difficulty)
            
            if local_ai_only:
                conditions.append("local_ai = 1")
            
            if tags:
                for tag in tags:
                    conditions.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            sql = f"""
                SELECT * FROM workflows 
                WHERE {where_clause}
                ORDER BY popularity_score DESC, name ASC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories with workflow counts"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT category, COUNT(*) as workflow_count
                FROM workflows
                GROUP BY category
                ORDER BY category
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_workflow_count(self) -> int:
        """Get total workflow count"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM workflows") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def update_workflow_stats(
        self, workflow_id: str, import_count: int = None, success_rate: float = None
    ):
        """Update workflow statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            updates = []
            params = []
            
            if import_count is not None:
                updates.append("import_count = ?")
                params.append(import_count)
            
            if success_rate is not None:
                updates.append("success_rate = ?")
                params.append(success_rate)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.utcnow().isoformat())
                params.append(workflow_id)
                
                sql = f"UPDATE workflows SET {', '.join(updates)} WHERE id = ?"
                await db.execute(sql, params)
                await db.commit()
