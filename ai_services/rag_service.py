"""
RAG (Retrieval Augmented Generation) service for UDCPR AI Assistant.
Uses vector search + OpenAI to answer questions about regulations.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from dotenv import load_dotenv
from vector_store import RuleVectorStore

load_dotenv()

app = FastAPI(title="UDCPR RAG Service", version="1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector store
vector_store = RuleVectorStore()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class QueryRequest(BaseModel):
    """Request model for AI queries."""
    query: str
    jurisdiction: Optional[str] = None
    project_context: Optional[dict] = None
    n_results: int = 5

class QueryResponse(BaseModel):
    """Response model for AI queries."""
    answer: str
    sources: List[dict]
    confidence: str
    follow_up_questions: List[str]

@app.get("/")
def root():
    """Health check."""
    return {
        "service": "UDCPR RAG Service",
        "version": "1.0",
        "status": "running",
        "vector_store_stats": vector_store.get_stats()
    }

@app.get("/health")
def health():
    """Health check endpoint."""
    stats = vector_store.get_stats()
    return {
        "status": "healthy",
        "vector_store_indexed": stats['indexed'],
        "total_rules": stats['total_rules']
    }

@app.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest):
    """
    Query the AI assistant about UDCPR/Mumbai DCPR regulations.
    
    Uses RAG to:
    1. Search vector store for relevant rules
    2. Pass context to OpenAI
    3. Generate accurate, cited answer
    """
    try:
        # Step 1: Retrieve relevant rules
        relevant_rules = vector_store.search(
            query=request.query,
            n_results=request.n_results,
            filter_jurisdiction=request.jurisdiction
        )
        
        if not relevant_rules:
            return QueryResponse(
                answer="I couldn't find any relevant regulations for your query. Please try rephrasing your question.",
                sources=[],
                confidence="low",
                follow_up_questions=[]
            )
        
        # Step 2: Prepare context for LLM
        context = _prepare_context(relevant_rules, request.project_context)
        
        # Step 3: Generate answer with OpenAI
        answer, confidence = await _generate_answer(request.query, context)
        
        # Step 4: Format sources
        sources = _format_sources(relevant_rules)
        
        # Step 5: Generate follow-up questions
        follow_ups = _generate_follow_ups(request.query, answer)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            follow_up_questions=follow_ups
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _prepare_context(rules: List[dict], project_context: Optional[dict] = None) -> str:
    """Prepare context string for LLM."""
    context_parts = []
    
    # Add project context if provided
    if project_context:
        context_parts.append("PROJECT CONTEXT:")
        context_parts.append(f"- Use Type: {project_context.get('use_type', 'N/A')}")
        context_parts.append(f"- Plot Area: {project_context.get('plot_area_sqm', 'N/A')} sqm")
        context_parts.append(f"- Road Width: {project_context.get('road_width_m', 'N/A')} m")
        context_parts.append("")
    
    # Add relevant rules
    context_parts.append("RELEVANT REGULATIONS:")
    context_parts.append("")
    
    for i, rule in enumerate(rules, 1):
        metadata = rule['metadata']
        context_parts.append(f"[{i}] {metadata.get('title', 'Untitled')}")
        context_parts.append(f"    Clause: {metadata.get('clause_number', 'N/A')}")
        context_parts.append(f"    Jurisdiction: {metadata.get('jurisdiction', 'N/A')}")
        if metadata.get('chapter'):
            context_parts.append(f"    Chapter: {metadata['chapter']}")
        context_parts.append(f"    Text: {rule['text'][:500]}...")
        context_parts.append("")
    
    return "\n".join(context_parts)

async def _generate_answer(query: str, context: str) -> tuple[str, str]:
    """Generate answer using OpenAI."""
    
    system_prompt = """You are an expert assistant for UDCPR (Unified Development Control and Promotion Regulations) and Mumbai DCPR regulations.

Your role:
- Answer questions accurately based on the provided regulations
- Always cite specific clause numbers
- Explain complex regulations in simple terms
- Highlight important conditions and exceptions
- If information is ambiguous or incomplete, say so

Format your answers:
1. Direct answer to the question
2. Relevant clause citations
3. Important conditions or exceptions
4. Practical implications

Be concise but comprehensive."""

    user_prompt = f"""Based on the following regulations, answer this question:

QUESTION: {query}

{context}

Provide a clear, accurate answer with clause citations."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        answer = response.choices[0].message.content
        
        # Determine confidence based on response
        confidence = "high" if len(context) > 500 else "medium"
        
        return answer, confidence
        
    except Exception as e:
        return f"Error generating answer: {str(e)}", "low"

def _format_sources(rules: List[dict]) -> List[dict]:
    """Format sources for response."""
    sources = []
    for rule in rules:
        metadata = rule['metadata']
        sources.append({
            "rule_id": metadata.get('rule_id', ''),
            "title": metadata.get('title', 'Untitled'),
            "clause_number": metadata.get('clause_number', 'N/A'),
            "jurisdiction": metadata.get('jurisdiction', ''),
            "chapter": metadata.get('chapter', '')
        })
    return sources

def _generate_follow_ups(query: str, answer: str) -> List[str]:
    """Generate follow-up questions."""
    # Simple rule-based follow-ups
    follow_ups = []
    
    if "fsi" in query.lower():
        follow_ups.extend([
            "What bonuses are available for FSI?",
            "How is premium FSI calculated?"
        ])
    elif "parking" in query.lower():
        follow_ups.extend([
            "What are the ECS requirements?",
            "Is mechanical parking allowed?"
        ])
    elif "setback" in query.lower():
        follow_ups.extend([
            "Are there relaxations for corner plots?",
            "How does building height affect setbacks?"
        ])
    else:
        follow_ups.extend([
            "What are the compliance requirements?",
            "Are there any special provisions?"
        ])
    
    return follow_ups[:3]

@app.get("/stats")
def get_stats():
    """Get vector store statistics."""
    return vector_store.get_stats()

if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("Starting UDCPR RAG Service...")
    print("="*70)
    print()
    
    # Check if vector store is indexed
    stats = vector_store.get_stats()
    if stats['total_rules'] == 0:
        print("⚠️  WARNING: Vector store is empty!")
        print("   Run: python vector_store.py to index rules first")
        print()
    else:
        print(f"✓ Vector store ready: {stats['total_rules']:,} rules indexed")
        print()
    
    print("Starting server...")
    print("  URL: http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
