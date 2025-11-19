"""
Vector store for UDCPR rules using ChromaDB.
Enables semantic search across all regulations.
"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
import json
from typing import List, Dict, Any
import os

class RuleVectorStore:
    """Vector store for UDCPR rules."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client."""
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="udcpr_rules",
            metadata={"description": "UDCPR and Mumbai DCPR regulations"}
        )
        
        print(f"Vector store initialized: {self.collection.count()} rules indexed")
    
    def index_rules(self, rules_directory: str):
        """Index all rules from approved_rules directory."""
        rules_dir = Path(rules_directory)
        
        if not rules_dir.exists():
            print(f"❌ Rules directory not found: {rules_directory}")
            return
        
        rule_files = list(rules_dir.glob("*.json"))
        print(f"\nIndexing {len(rule_files)} rules...")
        
        # Prepare data for batch insertion
        documents = []
        metadatas = []
        ids = []
        
        for i, rule_file in enumerate(rule_files):
            if i % 100 == 0:
                print(f"  Processing {i}/{len(rule_files)}...")
            
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rule = json.load(f)
                
                # Create searchable document text
                doc_text = self._create_document_text(rule)
                
                # Create metadata
                metadata = {
                    "rule_id": rule.get("rule_id", ""),
                    "title": rule.get("title", "")[:500],  # Limit length
                    "jurisdiction": rule.get("jurisdiction", ""),
                    "clause_number": rule.get("clause_number", ""),
                    "chapter": rule.get("chapter", "")[:200] if rule.get("chapter") else "",
                    "source_file": rule.get("source_pdf", {}).get("filename", "")
                }
                
                documents.append(doc_text)
                metadatas.append(metadata)
                ids.append(rule.get("rule_id", f"rule_{i}"))
                
            except Exception as e:
                print(f"  ⚠️  Error processing {rule_file.name}: {e}")
                continue
        
        # Batch insert into ChromaDB
        if documents:
            print(f"\n  Inserting {len(documents)} rules into vector store...")
            
            # ChromaDB has a batch size limit, so we'll insert in chunks
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                end_idx = min(i + batch_size, len(documents))
                
                self.collection.add(
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
                
                print(f"  Inserted batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
            print(f"\nSuccessfully indexed {len(documents)} rules")
            print(f"Total rules in vector store: {self.collection.count()}")
        else:
            print("❌ No rules to index")
    
    def _create_document_text(self, rule: Dict[str, Any]) -> str:
        """Create searchable text from rule."""
        parts = []
        
        # Add title
        if rule.get("title"):
            parts.append(f"Title: {rule['title']}")
        
        # Add clause number
        if rule.get("clause_number"):
            parts.append(f"Clause: {rule['clause_number']}")
        
        # Add chapter/section context
        if rule.get("chapter"):
            parts.append(f"Chapter: {rule['chapter']}")
        
        if rule.get("section"):
            parts.append(f"Section: {rule['section']}")
        
        # Add main clause text
        if rule.get("clause_text"):
            parts.append(f"Text: {rule['clause_text']}")
        
        # Add jurisdiction
        if rule.get("jurisdiction"):
            jurisdiction_name = "Maharashtra UDCPR" if rule["jurisdiction"] == "maharashtra_udcpr" else "Mumbai DCPR"
            parts.append(f"Jurisdiction: {jurisdiction_name}")
        
        return "\n".join(parts)
    
    def search(self, query: str, n_results: int = 5, filter_jurisdiction: str = None) -> List[Dict[str, Any]]:
        """Search for relevant rules using semantic search."""
        where_filter = None
        if filter_jurisdiction:
            where_filter = {"jurisdiction": filter_jurisdiction}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "rule_id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        total_count = self.collection.count()
        
        # Count by jurisdiction (sample-based)
        sample_size = min(1000, total_count)
        if sample_size > 0:
            sample = self.collection.get(limit=sample_size)
            udcpr_count = sum(1 for m in sample['metadatas'] if m.get('jurisdiction') == 'maharashtra_udcpr')
            mumbai_count = sum(1 for m in sample['metadatas'] if m.get('jurisdiction') == 'mumbai_dcpr')
            
            # Extrapolate
            ratio = total_count / sample_size
            udcpr_estimate = int(udcpr_count * ratio)
            mumbai_estimate = int(mumbai_count * ratio)
        else:
            udcpr_estimate = 0
            mumbai_estimate = 0
        
        return {
            "total_rules": total_count,
            "udcpr_rules": udcpr_estimate,
            "mumbai_dcpr_rules": mumbai_estimate,
            "indexed": total_count > 0
        }

# CLI for indexing
if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("UDCPR Master - Vector Store Indexing")
    print("="*70)
    print()
    
    # Initialize vector store
    store = RuleVectorStore()
    
    # Check if already indexed
    stats = store.get_stats()
    if stats['total_rules'] > 0:
        print(f"⚠️  Vector store already contains {stats['total_rules']} rules")
        response = input("Re-index all rules? (y/n): ")
        if response.lower() != 'y':
            print("Skipping indexing.")
            sys.exit(0)
        
        # Clear existing collection
        print("Clearing existing collection...")
        store.client.delete_collection("udcpr_rules")
        store.collection = store.client.create_collection(
            name="udcpr_rules",
            metadata={"description": "UDCPR and Mumbai DCPR regulations"}
        )
    
    # Index rules
    rules_dir = Path("../udcpr_master_data/approved_rules")
    if not rules_dir.exists():
        rules_dir = Path("udcpr_master_data/approved_rules")
    
    store.index_rules(str(rules_dir))
    
    # Show stats
    print("\n" + "="*70)
    print("INDEXING COMPLETE")
    print("="*70)
    stats = store.get_stats()
    print(f"\nVector Store Statistics:")
    print(f"  Total Rules: {stats['total_rules']:,}")
    print(f"  UDCPR Rules: ~{stats['udcpr_rules']:,}")
    print(f"  Mumbai DCPR Rules: ~{stats['mumbai_dcpr_rules']:,}")
    print()
    
    # Test search
    print("Testing semantic search...")
    test_queries = [
        "What is the FSI for residential buildings?",
        "Parking requirements for commercial buildings",
        "Setback requirements for corner plots"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = store.search(query, n_results=2)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['metadata']['title'][:60]}...")
            print(f"     Clause: {result['metadata']['clause_number']}")
    
    print("\n✓ Vector store ready for RAG service!")
