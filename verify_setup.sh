#!/bin/bash

echo "🔍 Pozi AI Studio - Environment Verification"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo "📦 Checking Docker..."
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker is running"
else
    echo -e "${RED}✗${NC} Docker is not running"
    exit 1
fi
echo ""

# Count running containers
CONTAINER_COUNT=$(docker ps --filter "name=localai" --filter "name=supabase" --filter "name=n8n" --filter "name=ollama" --filter "name=open-webui" --filter "name=flowise" --filter "name=qdrant" --filter "name=neo4j" --filter "name=caddy" --filter "name=redis" --filter "name=searxng" --filter "name=langfuse" --filter "name=clickhouse" --filter "name=minio" --filter "name=postgres" --format "{{.Names}}" | wc -l)
echo "🐳 Running Containers: $CONTAINER_COUNT"
echo ""

# Check key services
echo "🔧 Checking Key Services..."
echo ""

check_service() {
    SERVICE=$1
    if docker ps --format "{{.Names}}" | grep -q "^${SERVICE}$"; then
        STATUS=$(docker ps --format "{{.Names}}\t{{.Status}}" | grep "^${SERVICE}" | awk '{print $2}')
        echo -e "${GREEN}✓${NC} $SERVICE - $STATUS"
        return 0
    else
        echo -e "${RED}✗${NC} $SERVICE - Not running"
        return 1
    fi
}

check_service "n8n"
check_service "ollama"
check_service "open-webui"
check_service "flowise"
check_service "qdrant"
check_service "supabase-db"
check_service "supabase-studio"
check_service "caddy"
check_service "localai-neo4j-1"
check_service "localai-langfuse-web-1"
check_service "searxng"
check_service "redis"

echo ""
echo "🤖 Checking Ollama Models..."
MODELS=$(docker exec ollama ollama list 2>/dev/null | tail -n +2)
if [ -n "$MODELS" ]; then
    echo -e "${GREEN}✓${NC} Ollama models available:"
    echo "$MODELS" | while read line; do
        echo "  - $line"
    done
else
    echo -e "${YELLOW}⚠${NC} No Ollama models found"
fi

echo ""
echo "🌐 Checking Service Endpoints..."
echo ""

check_endpoint() {
    SERVICE=$1
    PORT=$2
    CONTAINER=$3
    
    if docker exec $CONTAINER curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT > /dev/null 2>&1; then
        HTTP_CODE=$(docker exec $CONTAINER curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT 2>/dev/null)
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "401" ]; then
            echo -e "${GREEN}✓${NC} $SERVICE (port $PORT) - HTTP $HTTP_CODE"
        else
            echo -e "${YELLOW}⚠${NC} $SERVICE (port $PORT) - HTTP $HTTP_CODE"
        fi
    else
        echo -e "${RED}✗${NC} $SERVICE (port $PORT) - Not responding"
    fi
}

# Check internal endpoints
check_endpoint "n8n" "5678" "n8n"
check_endpoint "Ollama" "11434" "ollama"
check_endpoint "Qdrant" "6333" "qdrant"

echo ""
echo "🔑 Checking Credentials..."
echo ""

if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check for required variables
    REQUIRED_VARS=("N8N_ENCRYPTION_KEY" "POSTGRES_PASSWORD" "JWT_SECRET" "NEO4J_AUTH" "OPENROUTER_API_KEY" "PERPLEXITY_API_KEY" "GEMINI_API_KEY")
    
    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${VAR}=" .env && ! grep -q "^${VAR}=$" .env && ! grep -q "^${VAR}=your-" .env; then
            echo -e "${GREEN}✓${NC} $VAR is set"
        else
            echo -e "${RED}✗${NC} $VAR is not set or using default value"
        fi
    done
else
    echo -e "${RED}✗${NC} .env file not found"
fi

echo ""
echo "📊 Resource Usage..."
echo ""
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10

echo ""
echo "🌐 Access URLs (Gitpod Ports)..."
echo ""
echo "Check your Gitpod PORTS tab for these services:"
echo "  • n8n:           Port 8001"
echo "  • Open WebUI:    Port 8002"
echo "  • Flowise:       Port 8003"
echo "  • Supabase:      Port 8005"
echo "  • Langfuse:      Port 8007"
echo "  • Neo4j:         Port 8008"
echo ""
echo "Make sure to set ports to 'Public' visibility!"
echo ""

echo "=============================================="
echo "✅ Verification Complete!"
echo ""
echo "📖 Next Steps:"
echo "  1. Check CONFIGURATION_GUIDE.md for detailed setup"
echo "  2. Access n8n (port 8001) to create your account"
echo "  3. Configure credentials in n8n"
echo "  4. Test the pre-loaded RAG workflows"
echo ""
