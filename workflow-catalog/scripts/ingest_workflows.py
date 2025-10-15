#!/usr/bin/env python3
"""
CLI script to ingest workflows from GitHub repositories
"""
import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Database
from app.services.ingestion import WorkflowIngestion


async def main():
    """Main ingestion workflow"""
    print("🚀 Starting workflow ingestion pipeline...")
    print("=" * 60)
    
    # Initialize services
    db = Database()
    ingestion = WorkflowIngestion()
    
    # Initialize database
    print("\n📊 Initializing database...")
    await db.init_db()
    print("✅ Database ready")
    
    # Ingest workflows from all repositories
    print("\n📦 Fetching workflows from GitHub repositories...")
    print("   - Zie619/n8n-workflows (2,057 workflows)")
    print("   - enescingoz/awesome-n8n-templates (curated)")
    print()
    
    # Limit to 50 workflows per repo for initial testing
    workflows = await ingestion.ingest_all_repos(max_per_repo=50)
    
    if not workflows:
        print("❌ No workflows found")
        return
    
    print(f"\n✅ Successfully fetched {len(workflows)} workflows")
    
    # Store workflows in database
    print("\n💾 Storing workflows in database...")
    stored_count = 0
    
    for i, workflow in enumerate(workflows, 1):
        if i % 10 == 0:
            print(f"   Stored {i}/{len(workflows)} workflows...")
        
        try:
            await db.insert_workflow(workflow)
            stored_count += 1
        except Exception as e:
            print(f"   ⚠️  Error storing workflow {workflow.get('name', 'unknown')}: {e}")
    
    print(f"✅ Stored {stored_count} workflows in database")
    
    # Generate summary
    print("\n📈 Ingestion Summary")
    print("=" * 60)
    
    summary = ingestion.generate_summary(workflows)
    
    print(f"Total Workflows: {summary['total_workflows']}")
    print(f"Local AI Workflows: {summary['local_ai_workflows']}")
    print(f"Avg Nodes per Workflow: {summary['avg_nodes_per_workflow']}")
    
    print("\n📂 Categories:")
    for cat, count in sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    print("\n🎯 Difficulty Distribution:")
    for diff, count in summary['difficulties'].items():
        print(f"   {diff.capitalize()}: {count}")
    
    print("\n✅ Compatibility Status:")
    for status, count in summary['compatibility_statuses'].items():
        print(f"   {status}: {count}")
    
    # Save summary to file
    summary_path = Path("data/ingestion_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Summary saved to {summary_path}")
    print("\n🎉 Ingestion complete!")


if __name__ == "__main__":
    asyncio.run(main())
