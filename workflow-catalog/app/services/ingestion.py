"""
Workflow ingestion pipeline - fetch and process workflows from GitHub
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import httpx
from .parser import WorkflowParser


class WorkflowIngestion:
    """Ingest workflows from GitHub repositories"""
    
    REPOS = {
        'Zie619/n8n-workflows': {
            'workflows_path': 'workflows',
            'branch': 'main',
        },
        'enescingoz/awesome-n8n-templates': {
            'workflows_path': '',  # Workflows in category folders
            'branch': 'main',
        },
    }
    
    def __init__(self, data_dir: str = "data/workflows"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.parser = WorkflowParser()
    
    async def fetch_repo_contents(self, repo: str, path: str = "") -> List[Dict]:
        """Fetch repository contents from GitHub API"""
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=30.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error fetching {url}: {response.status_code}")
                    return []
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return []
    
    async def download_workflow(self, download_url: str, save_path: Path) -> bool:
        """Download a workflow JSON file"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(download_url, timeout=30.0)
                if response.status_code == 200:
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    return True
                else:
                    print(f"Error downloading {download_url}: {response.status_code}")
                    return False
            except Exception as e:
                print(f"Error downloading {download_url}: {e}")
                return False
    
    async def ingest_repo(self, repo: str, max_workflows: int = None) -> List[Dict[str, Any]]:
        """Ingest workflows from a GitHub repository"""
        print(f"\n📦 Ingesting workflows from {repo}...")
        
        repo_config = self.REPOS.get(repo)
        if not repo_config:
            print(f"Unknown repository: {repo}")
            return []
        
        workflows = []
        workflows_path = repo_config['workflows_path']
        
        # Fetch repository structure
        contents = await self.fetch_repo_contents(repo, workflows_path)
        
        # Process contents
        workflow_files = []
        for item in contents:
            if item['type'] == 'file' and item['name'].endswith('.json'):
                workflow_files.append(item)
            elif item['type'] == 'dir':
                # Recursively fetch from subdirectories
                subdir_contents = await self.fetch_repo_contents(repo, item['path'])
                for subitem in subdir_contents:
                    if subitem['type'] == 'file' and subitem['name'].endswith('.json'):
                        workflow_files.append(subitem)
        
        print(f"Found {len(workflow_files)} workflow files")
        
        # Limit if specified
        if max_workflows:
            workflow_files = workflow_files[:max_workflows]
            print(f"Processing first {max_workflows} workflows")
        
        # Download and parse workflows
        for i, file_info in enumerate(workflow_files, 1):
            if i % 10 == 0:
                print(f"Processing workflow {i}/{len(workflow_files)}...")
            
            # Download workflow
            repo_name = repo.split('/')[1]
            save_path = self.data_dir / repo_name / file_info['path']
            
            if not save_path.exists():
                success = await self.download_workflow(file_info['download_url'], save_path)
                if not success:
                    continue
            
            # Parse workflow
            workflow = self.parser.parse_workflow(save_path, repo)
            if workflow:
                workflow['source_url'] = file_info['html_url']
                workflows.append(workflow)
        
        print(f"✅ Successfully processed {len(workflows)} workflows from {repo}")
        return workflows
    
    async def ingest_all_repos(self, max_per_repo: int = 50) -> List[Dict[str, Any]]:
        """Ingest workflows from all configured repositories"""
        all_workflows = []
        
        for repo in self.REPOS.keys():
            workflows = await self.ingest_repo(repo, max_per_repo)
            all_workflows.extend(workflows)
        
        return all_workflows
    
    def generate_summary(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate ingestion summary statistics"""
        if not workflows:
            return {}
        
        categories = {}
        difficulties = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        compatibility_statuses = {}
        local_ai_count = 0
        total_nodes = 0
        
        for wf in workflows:
            # Categories
            cat = wf['category']
            categories[cat] = categories.get(cat, 0) + 1
            
            # Difficulty
            diff = wf['difficulty']
            difficulties[diff] += 1
            
            # Compatibility
            status = wf['compatibility']['status']
            compatibility_statuses[status] = compatibility_statuses.get(status, 0) + 1
            
            # Local AI
            if wf['compatibility']['local_ai']:
                local_ai_count += 1
            
            # Nodes
            total_nodes += wf['metadata']['node_count']
        
        return {
            'total_workflows': len(workflows),
            'categories': categories,
            'difficulties': difficulties,
            'compatibility_statuses': compatibility_statuses,
            'local_ai_workflows': local_ai_count,
            'avg_nodes_per_workflow': round(total_nodes / len(workflows), 1),
        }
