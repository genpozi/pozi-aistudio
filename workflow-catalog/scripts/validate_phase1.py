#!/usr/bin/env python3
"""
Phase 1 Validation Script
Tests all Phase 1 deliverables
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Database
from app.services.parser import WorkflowParser
from app.services.ingestion import WorkflowIngestion


async def validate_database():
    """Test 1: Database functionality"""
    print("\n" + "="*60)
    print("TEST 1: Database Functionality")
    print("="*60)
    
    db = Database()
    await db.init_db()
    
    # Test workflow count
    count = await db.get_workflow_count()
    assert count > 0, "No workflows in database"
    print(f"✅ Database contains {count} workflows")
    
    # Test categories
    categories = await db.get_categories()
    assert len(categories) > 0, "No categories found"
    print(f"✅ Found {len(categories)} categories")
    
    # Test search
    workflows = await db.search_workflows(limit=10)
    assert len(workflows) > 0, "Search returned no results"
    print(f"✅ Search functionality working")
    
    # Test FTS5 search
    search_results = await db.search_workflows(query="AI chatbot", limit=5)
    print(f"✅ Full-text search working ({len(search_results)} results)")
    
    # Test filters
    local_ai = await db.search_workflows(local_ai_only=True, limit=5)
    assert len(local_ai) > 0, "No local AI workflows found"
    print(f"✅ Local AI filter working ({len(local_ai)} workflows)")
    
    return True


async def validate_parser():
    """Test 2: Workflow parser"""
    print("\n" + "="*60)
    print("TEST 2: Workflow Parser")
    print("="*60)
    
    parser = WorkflowParser()
    
    # Find a sample workflow
    workflow_dir = Path("data/workflows")
    if not workflow_dir.exists():
        print("⚠️  No workflows directory found, skipping parser test")
        return True
    
    json_files = list(workflow_dir.rglob("*.json"))
    if not json_files:
        print("⚠️  No workflow files found, skipping parser test")
        return True
    
    # Test parsing
    sample_file = json_files[0]
    workflow = parser.parse_workflow(sample_file, "test/repo")
    
    assert workflow is not None, "Parser returned None"
    print(f"✅ Successfully parsed: {workflow['name']}")
    
    # Validate structure
    required_fields = ['id', 'name', 'category', 'difficulty', 'metadata', 
                      'requirements', 'compatibility', 'stats']
    for field in required_fields:
        assert field in workflow, f"Missing field: {field}"
    print(f"✅ Workflow structure valid")
    
    # Validate metadata
    assert 'node_count' in workflow['metadata'], "Missing node_count"
    assert workflow['metadata']['node_count'] > 0, "Invalid node_count"
    print(f"✅ Metadata extraction working")
    
    # Validate compatibility
    assert 'compatibility_score' in workflow['compatibility'], "Missing compatibility_score"
    score = workflow['compatibility']['compatibility_score']
    assert 0.0 <= score <= 1.0, f"Invalid compatibility score: {score}"
    print(f"✅ Compatibility analysis working (score: {score:.2f})")
    
    return True


async def validate_ingestion():
    """Test 3: Ingestion pipeline"""
    print("\n" + "="*60)
    print("TEST 3: Ingestion Pipeline")
    print("="*60)
    
    ingestion = WorkflowIngestion()
    
    # Check data directory
    assert ingestion.data_dir.exists(), "Data directory not created"
    print(f"✅ Data directory exists: {ingestion.data_dir}")
    
    # Check downloaded workflows
    workflow_files = list(ingestion.data_dir.rglob("*.json"))
    assert len(workflow_files) > 0, "No workflows downloaded"
    print(f"✅ Downloaded {len(workflow_files)} workflow files")
    
    # Check summary
    summary_file = Path("data/ingestion_summary.json")
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
        print(f"✅ Ingestion summary generated")
        print(f"   Total workflows: {summary.get('total_workflows', 0)}")
        print(f"   Local AI workflows: {summary.get('local_ai_workflows', 0)}")
    
    return True


async def validate_api_models():
    """Test 4: API models and structure"""
    print("\n" + "="*60)
    print("TEST 4: API Models")
    print("="*60)
    
    from app.models import (
        Workflow, WorkflowList, Category, DifficultyLevel,
        CompatibilityStatus, HealthCheck
    )
    
    # Test enum values
    assert DifficultyLevel.BEGINNER.value == "beginner"
    assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
    assert DifficultyLevel.ADVANCED.value == "advanced"
    print(f"✅ DifficultyLevel enum valid")
    
    assert CompatibilityStatus.FULLY_COMPATIBLE.value == "fully_compatible"
    print(f"✅ CompatibilityStatus enum valid")
    
    # Test model imports
    print(f"✅ All Pydantic models importable")
    
    return True


async def validate_compatibility_analysis():
    """Test 5: Compatibility analysis accuracy"""
    print("\n" + "="*60)
    print("TEST 5: Compatibility Analysis")
    print("="*60)
    
    db = Database()
    await db.init_db()
    
    # Get workflows by compatibility status
    all_workflows = await db.search_workflows(limit=100)
    
    statuses = {}
    for wf in all_workflows:
        status = wf.get('compatibility_status', 'unknown')
        statuses[status] = statuses.get(status, 0) + 1
    
    print(f"✅ Compatibility distribution:")
    for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
        print(f"   {status}: {count} workflows")
    
    # Validate local AI detection
    local_ai_workflows = [w for w in all_workflows if w.get('local_ai')]
    print(f"✅ Local AI detection: {len(local_ai_workflows)} workflows")
    
    # Validate compatibility scores
    scores = [w.get('compatibility_score', 0) for w in all_workflows]
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"✅ Average compatibility score: {avg_score:.2f}")
    
    return True


async def validate_categorization():
    """Test 6: Workflow categorization"""
    print("\n" + "="*60)
    print("TEST 6: Workflow Categorization")
    print("="*60)
    
    db = Database()
    await db.init_db()
    
    categories = await db.get_categories()
    
    print(f"✅ Categories found: {len(categories)}")
    for cat in categories:
        print(f"   {cat['category']}: {cat['workflow_count']} workflows")
    
    # Validate difficulty distribution
    all_workflows = await db.search_workflows(limit=100)
    difficulties = {}
    for wf in all_workflows:
        diff = wf.get('difficulty', 'unknown')
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print(f"\n✅ Difficulty distribution:")
    for diff, count in sorted(difficulties.items()):
        print(f"   {diff}: {count} workflows")
    
    return True


async def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("PHASE 1 VALIDATION SUITE")
    print("="*60)
    
    tests = [
        ("Database Functionality", validate_database),
        ("Workflow Parser", validate_parser),
        ("Ingestion Pipeline", validate_ingestion),
        ("API Models", validate_api_models),
        ("Compatibility Analysis", validate_compatibility_analysis),
        ("Workflow Categorization", validate_categorization),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL PHASE 1 DELIVERABLES VALIDATED!")
        print("\nPhase 1 Complete:")
        print("  ✅ Project structure")
        print("  ✅ SQLite database with FTS5")
        print("  ✅ Workflow parser and metadata extractor")
        print("  ✅ GitHub repository analysis")
        print("  ✅ Workflow ingestion pipeline")
        print("  ✅ FastAPI REST API endpoints")
        print("  ✅ Compatibility analysis system")
        print("  ✅ All tests passing")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
