#!/bin/bash

echo "🤖 Testing Ollama Setup"
echo "======================="
echo ""

# Test Ollama is running
echo "1. Checking Ollama service..."
if docker ps | grep -q ollama; then
    echo "✓ Ollama container is running"
else
    echo "✗ Ollama container is not running"
    exit 1
fi
echo ""

# List available models
echo "2. Available models:"
docker exec ollama ollama list
echo ""

# Test chat completion
echo "3. Testing chat completion with qwen2.5..."
echo "   Prompt: 'Say hello in 5 words or less'"
echo ""
docker exec ollama ollama run qwen2.5:7b-instruct-q4_K_M "Say hello in 5 words or less" 2>/dev/null
echo ""

# Test embeddings
echo "4. Testing embeddings with nomic-embed-text..."
EMBEDDING_RESULT=$(docker exec ollama curl -s http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "Hello world"
}' 2>/dev/null)

if echo "$EMBEDDING_RESULT" | grep -q "embedding"; then
    EMBEDDING_LENGTH=$(echo "$EMBEDDING_RESULT" | grep -o "embedding" | wc -l)
    echo "✓ Embeddings working (response contains embedding data)"
else
    echo "✗ Embeddings test failed"
fi
echo ""

# Test API endpoint
echo "5. Testing Ollama API endpoint..."
API_RESPONSE=$(docker exec ollama curl -s http://localhost:11434/api/tags 2>/dev/null)
if echo "$API_RESPONSE" | grep -q "models"; then
    echo "✓ Ollama API is responding"
else
    echo "✗ Ollama API is not responding"
fi
echo ""

echo "======================="
echo "✅ Ollama tests complete!"
echo ""
echo "You can now use Ollama in n8n with:"
echo "  Base URL: http://ollama:11434"
echo "  Models: qwen2.5:7b-instruct-q4_K_M, nomic-embed-text"
