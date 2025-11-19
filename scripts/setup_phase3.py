#!/usr/bin/env python3
"""
Setup script for Phase 3 - RAG Service + AI Assistant.
"""
import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("="*70)
    print("PHASE 3 SETUP - RAG Service + AI Assistant")
    print("="*70)
    print()
    
    # Step 1: Install Python dependencies
    print("1. Installing Python dependencies for AI services...")
    print("-"*70)
    
    success, stdout, stderr = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        cwd="ai_services"
    )
    
    if success:
        print("✓ Python dependencies installed")
    else:
        print(f"✗ Failed to install dependencies")
        print(stderr)
        return 1
    
    print()
    
    # Step 2: Check OpenAI API key
    print("2. Checking OpenAI API key...")
    print("-"*70)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and len(api_key) > 20:
        print(f"✓ OpenAI API key found: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("⚠️  OpenAI API key not found or invalid")
        print("   Set OPENAI_API_KEY in .env file")
        print("   Example: OPENAI_API_KEY=sk-...")
    
    print()
    
    # Step 3: Index rules in vector store
    print("3. Indexing rules in vector store...")
    print("-"*70)
    print("   This will create embeddings for all 6,000+ rules")
    print("   Estimated time: 2-5 minutes")
    print()
    
    response = input("   Proceed with indexing? (y/n): ")
    if response.lower() == 'y':
        print("\n   Indexing...")
        success, stdout, stderr = run_command(
            f"{sys.executable} vector_store.py",
            cwd="ai_services"
        )
        
        if success:
            print("✓ Vector store indexed successfully")
            print(stdout[-500:] if len(stdout) > 500 else stdout)
        else:
            print("✗ Indexing failed")
            print(stderr[-500:] if len(stderr) > 500 else stderr)
    else:
        print("   Skipped indexing")
    
    print()
    
    # Step 4: Summary
    print("="*70)
    print("PHASE 3 SETUP COMPLETE")
    print("="*70)
    print()
    print("Next steps:")
    print()
    print("1. Start RAG Service:")
    print("   cd ai_services")
    print("   python rag_service.py")
    print("   (Runs on http://localhost:8000)")
    print()
    print("2. Start Backend (in another terminal):")
    print("   cd backend")
    print("   npm start")
    print()
    print("3. Start Frontend (in another terminal):")
    print("   cd frontend")
    print("   npm start")
    print()
    print("4. Access AI Assistant:")
    print("   http://localhost:3000/ai-assistant")
    print()
    print("Try asking:")
    print("  • What is the FSI for residential buildings?")
    print("  • Parking requirements for commercial buildings")
    print("  • Setback rules for corner plots")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
