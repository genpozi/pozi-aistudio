"""
Workflow JSON parser and metadata extractor
"""
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from datetime import datetime


class WorkflowParser:
    """Parse n8n workflow JSON files and extract metadata"""
    
    # Known local services in Pozi AI Studio
    LOCAL_SERVICES = {
        'ollama', 'postgres', 'qdrant', 'supabase', 'neo4j',
        'langfuse', 'flowise', 'redis', 'minio', 'clickhouse'
    }
    
    # Node types that indicate local AI usage
    LOCAL_AI_NODES = {
        '@n8n/n8n-nodes-langchain.agent',
        '@n8n/n8n-nodes-langchain.chainLlm',
        '@n8n/n8n-nodes-langchain.chainSummarization',
        '@n8n/n8n-nodes-langchain.chainRetrievalQa',
        '@n8n/n8n-nodes-langchain.lmChatOllama',
        '@n8n/n8n-nodes-langchain.lmOllama',
        '@n8n/n8n-nodes-langchain.embeddingsOllama',
    }
    
    def parse_workflow(self, json_path: Path, source_repo: str) -> Optional[Dict[str, Any]]:
        """Parse a workflow JSON file and extract all metadata"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # Extract basic info
            workflow_id = str(uuid.uuid4())
            name = workflow_data.get('name', json_path.stem)
            description = self._extract_description(workflow_data)
            
            # Extract nodes and analyze
            nodes = workflow_data.get('nodes', [])
            node_analysis = self._analyze_nodes(nodes)
            
            # Determine category and difficulty
            category, subcategory = self._categorize_workflow(name, description, node_analysis)
            difficulty = self._determine_difficulty(node_analysis)
            
            # Extract requirements
            requirements = self._extract_requirements(nodes, node_analysis)
            
            # Analyze compatibility
            compatibility = self._analyze_compatibility(requirements, node_analysis)
            
            # Extract tags
            tags = self._extract_tags(workflow_data, name, description, node_analysis)
            
            # Build workflow object
            workflow = {
                'id': workflow_id,
                'name': name,
                'description': description,
                'category': category,
                'subcategory': subcategory,
                'difficulty': difficulty,
                'author': self._extract_author(source_repo),
                'source_repo': source_repo,
                'source_url': None,  # Will be set by ingestion pipeline
                'json_path': str(json_path),
                'tags': tags,
                'department': self._determine_department(category, tags),
                'use_cases': self._extract_use_cases(name, description, category),
                
                'metadata': {
                    'node_count': len(nodes),
                    'integrations': node_analysis['integrations'],
                    'node_types': node_analysis['node_types'],
                    'has_webhook': node_analysis['has_webhook'],
                    'has_schedule': node_analysis['has_schedule'],
                    'estimated_runtime': self._estimate_runtime(node_analysis),
                },
                
                'requirements': requirements,
                'compatibility': compatibility,
                
                'stats': {
                    'popularity_score': 0,
                    'import_count': 0,
                    'success_rate': 0.0,
                    'avg_setup_time': None,
                },
                
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'last_synced': None,
            }
            
            return workflow
            
        except Exception as e:
            print(f"Error parsing workflow {json_path}: {e}")
            return None
    
    def _extract_description(self, workflow_data: Dict) -> Optional[str]:
        """Extract workflow description from various sources"""
        # Check for description in workflow data
        if 'description' in workflow_data:
            return workflow_data['description']
        
        # Check for sticky notes that might contain description
        nodes = workflow_data.get('nodes', [])
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.stickyNote':
                content = node.get('parameters', {}).get('content', '')
                if content and len(content) > 20:
                    return content[:500]  # First 500 chars
        
        return None
    
    def _analyze_nodes(self, nodes: List[Dict]) -> Dict[str, Any]:
        """Analyze workflow nodes to extract metadata"""
        integrations: Set[str] = set()
        node_types: Set[str] = set()
        has_webhook = False
        has_schedule = False
        has_local_ai = False
        credential_types: Set[str] = set()
        
        for node in nodes:
            node_type = node.get('type', '')
            node_types.add(node_type)
            
            # Check for webhooks
            if 'webhook' in node_type.lower():
                has_webhook = True
            
            # Check for schedule/cron
            if 'schedule' in node_type.lower() or 'cron' in node_type.lower():
                has_schedule = True
            
            # Check for local AI nodes
            if node_type in self.LOCAL_AI_NODES:
                has_local_ai = True
            
            # Extract integration name from node type
            if node_type.startswith('n8n-nodes-base.'):
                integration = node_type.replace('n8n-nodes-base.', '').lower()
                integrations.add(integration)
            elif node_type.startswith('@n8n/'):
                # LangChain and other special nodes
                parts = node_type.split('.')
                if len(parts) > 1:
                    integrations.add(parts[-1].lower())
            
            # Extract credential types
            credentials = node.get('credentials', {})
            for cred_type in credentials.keys():
                credential_types.add(cred_type.lower())
        
        return {
            'integrations': sorted(list(integrations)),
            'node_types': sorted(list(node_types)),
            'has_webhook': has_webhook,
            'has_schedule': has_schedule,
            'has_local_ai': has_local_ai,
            'credential_types': sorted(list(credential_types)),
        }
    
    def _extract_requirements(self, nodes: List[Dict], node_analysis: Dict) -> Dict[str, Any]:
        """Extract workflow requirements"""
        credentials = []
        services = set()
        external_apis = set()
        
        # Analyze credential requirements
        for cred_type in node_analysis['credential_types']:
            is_local = any(svc in cred_type for svc in self.LOCAL_SERVICES)
            
            credentials.append({
                'type': cred_type,
                'required': True,
                'local': is_local,
                'description': None,
            })
            
            # Track services
            if is_local:
                for svc in self.LOCAL_SERVICES:
                    if svc in cred_type:
                        services.add(svc)
            else:
                external_apis.add(cred_type)
        
        return {
            'credentials': credentials,
            'services': sorted(list(services)),
            'external_apis': sorted(list(external_apis)),
            'min_n8n_version': '1.0.0',
        }
    
    def _analyze_compatibility(self, requirements: Dict, node_analysis: Dict) -> Dict[str, Any]:
        """Analyze workflow compatibility with Pozi AI Studio"""
        local_ai = node_analysis['has_local_ai']
        requires_external_api = len(requirements['external_apis']) > 0
        works_offline = not requires_external_api
        
        # Calculate compatibility score
        score = 1.0
        
        if requires_external_api:
            score -= 0.3
        
        if not local_ai and requires_external_api:
            score -= 0.3
        
        if len(requirements['services']) == 0:
            score -= 0.2
        
        # Determine status
        if score >= 0.8:
            status = 'fully_compatible'
        elif score >= 0.5:
            status = 'partially_compatible'
        elif requires_external_api:
            status = 'requires_external'
        else:
            status = 'incompatible'
        
        pozi_compatible = score >= 0.5
        
        return {
            'local_ai': local_ai,
            'requires_external_api': requires_external_api,
            'works_offline': works_offline,
            'pozi_compatible': pozi_compatible,
            'status': status,
            'compatibility_score': round(score, 2),
        }
    
    def _categorize_workflow(self, name: str, description: Optional[str], node_analysis: Dict) -> tuple:
        """Determine workflow category and subcategory"""
        text = f"{name} {description or ''}".lower()
        integrations = set(node_analysis['integrations'])
        
        # AI & Machine Learning
        if any(term in text for term in ['ai', 'rag', 'llm', 'gpt', 'agent', 'langchain']):
            if 'rag' in text or 'retrieval' in text:
                return ('AI & Machine Learning', 'RAG & Document Processing')
            elif 'agent' in text:
                return ('AI & Machine Learning', 'AI Agents')
            return ('AI & Machine Learning', 'General AI')
        
        # Communication
        if any(svc in integrations for svc in ['gmail', 'email', 'slack', 'telegram', 'discord', 'whatsapp']):
            if 'gmail' in integrations or 'email' in text:
                return ('Communication & Messaging', 'Email')
            elif 'slack' in integrations:
                return ('Communication & Messaging', 'Slack')
            elif 'telegram' in integrations:
                return ('Communication & Messaging', 'Telegram')
            return ('Communication & Messaging', 'General')
        
        # Data & Analytics
        if any(term in text for term in ['data', 'analytics', 'database', 'sql', 'etl']):
            return ('Data & Analytics', 'Data Processing')
        
        # Business & Productivity
        if any(term in text for term in ['business', 'productivity', 'automation', 'workflow']):
            return ('Business & Productivity', 'Automation')
        
        # Default
        return ('Utilities & Tools', 'General')
    
    def _determine_difficulty(self, node_analysis: Dict) -> str:
        """Determine workflow difficulty level"""
        node_count = len(node_analysis['node_types'])
        
        if node_count <= 5:
            return 'beginner'
        elif node_count <= 15:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _extract_tags(self, workflow_data: Dict, name: str, description: Optional[str], node_analysis: Dict) -> List[str]:
        """Extract relevant tags from workflow"""
        tags = set()
        
        # Add existing tags
        existing_tags = workflow_data.get('tags', [])
        if isinstance(existing_tags, list):
            tags.update(tag.get('name', '') if isinstance(tag, dict) else str(tag) for tag in existing_tags)
        
        # Add tags based on content
        text = f"{name} {description or ''}".lower()
        
        tag_keywords = {
            'ai': ['ai', 'artificial intelligence', 'machine learning'],
            'rag': ['rag', 'retrieval', 'augmented generation'],
            'automation': ['automation', 'automate', 'automatic'],
            'email': ['email', 'gmail', 'mail'],
            'chat': ['chat', 'messaging', 'conversation'],
            'document': ['document', 'pdf', 'file'],
            'data': ['data', 'database', 'sql'],
            'local': ['local', 'offline', 'self-hosted'],
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.add(tag)
        
        # Add integration tags
        for integration in node_analysis['integrations'][:5]:  # Top 5 integrations
            tags.add(integration)
        
        return sorted(list(tags))[:10]  # Max 10 tags
    
    def _determine_department(self, category: str, tags: List[str]) -> Optional[str]:
        """Determine which department would use this workflow"""
        if 'AI' in category:
            return 'Engineering'
        elif 'Communication' in category:
            return 'Operations'
        elif 'Data' in category:
            return 'Analytics'
        elif 'Business' in category:
            return 'Executive'
        return None
    
    def _extract_use_cases(self, name: str, description: Optional[str], category: str) -> List[str]:
        """Extract potential use cases"""
        use_cases = []
        text = f"{name} {description or ''}".lower()
        
        use_case_patterns = {
            'Document Q&A': ['document', 'q&a', 'question', 'answer'],
            'Email Automation': ['email', 'gmail', 'automate', 'respond'],
            'Data Processing': ['data', 'process', 'transform', 'etl'],
            'Chat Bot': ['chat', 'bot', 'conversation', 'assistant'],
            'Content Generation': ['generate', 'create', 'content', 'write'],
            'Research Assistant': ['research', 'analyze', 'summarize'],
        }
        
        for use_case, keywords in use_case_patterns.items():
            if sum(1 for kw in keywords if kw in text) >= 2:
                use_cases.append(use_case)
        
        return use_cases[:3]  # Max 3 use cases
    
    def _estimate_runtime(self, node_analysis: Dict) -> str:
        """Estimate workflow runtime"""
        node_count = len(node_analysis['node_types'])
        
        if node_count <= 5:
            return "< 1 minute"
        elif node_count <= 15:
            return "1-5 minutes"
        else:
            return "5+ minutes"
    
    def _extract_author(self, source_repo: str) -> str:
        """Extract author from source repo"""
        if '/' in source_repo:
            return source_repo.split('/')[0]
        return source_repo
