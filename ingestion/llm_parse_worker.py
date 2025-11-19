#!/usr/bin/env python3
"""
LLM-assisted parsing of OCR text into structured rule JSON.
Uses OpenAI with temperature=0 for deterministic parsing.
"""
import os
import json
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

WORK_DIR = Path("udcpr_master_data")
PDF_NAMES = [
    "UDCPR Updated 30.01.25 with earlier provisions & corrections_compressed",
    "MUBAI-DCPR"
]

SYSTEM_PROMPT = """You are a professional legal/regulation parser specializing in Indian building regulations.

Your task: Parse OCR text from UDCPR/DCPR documents into structured JSON.

Output format (JSON array of rule objects):
{
  "rule_id": "unique_id",
  "title": "Rule title",
  "jurisdiction": "maharashtra_udcpr or mumbai_dcpr",
  "clause_number": "e.g., 3.1.2",
  "clause_text": "Full clause text",
  "parsed": {
    "type": "rule|table|note",
    "rule_logic": {
      "conditions": [{"field": "road_width", "op": ">=", "value": 12, "units": "m"}],
      "outputs": [{"field": "front_setback", "value": 6, "units": "m"}]
    }
  },
  "ambiguous": false,
  "ambiguity_reason": null
}

Field names to use: road_width, plot_area_sqm, height_m, use_type, corner_plot, frontage_m, fsi, built_up_area_sqm, parking_slots, setback_front, setback_rear, setback_side.

If text is unclear or ambiguous, set "ambiguous": true and explain in "ambiguity_reason".

Return ONLY valid JSON array. No markdown, no explanations."""

def parse_page_with_llm(page_text: str, page_num: int, pdf_name: str) -> List[Dict]:
    """Parse a single page using OpenAI."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    user_prompt = f"""PDF: {pdf_name}
Page: {page_num}

OCR Text:
{page_text[:4000]}

Parse this into structured rule JSON array."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure it's an array
        if isinstance(result, dict) and "rules" in result:
            return result["rules"]
        elif isinstance(result, list):
            return result
        else:
            return [result]
            
    except Exception as e:
        print(f"    ❌ LLM error: {e}")
        return []

def process_pdf(pdf_name: str):
    """Process all pages of a PDF."""
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_name}")
    print(f"{'='*60}")
    
    text_dir = WORK_DIR / "raw_text" / pdf_name
    output_dir = WORK_DIR / "staging_rules"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not text_dir.exists():
        print(f"  ⚠️  No OCR text found. Run pdf_to_images_and_ocr.py first.")
        return
    
    all_candidates = []
    text_files = sorted(text_dir.glob("page_*.txt"))
    
    print(f"Found {len(text_files)} pages")
    
    for i, text_file in enumerate(text_files, start=1):
        print(f"  Page {i}/{len(text_files)}: Parsing...", end=" ")
        
        with open(text_file, 'r', encoding='utf-8') as f:
            page_text = f.read()
        
        if len(page_text.strip()) < 50:
            print("⊘ (empty)")
            continue
        
        candidates = parse_page_with_llm(page_text, i, pdf_name)
        all_candidates.extend(candidates)
        print(f"✓ ({len(candidates)} rules)")
        
        # Rate limiting
        time.sleep(0.5)
    
    # Save candidates
    timestamp = int(time.time())
    output_file = output_dir / f"{pdf_name}_candidates_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(all_candidates)} candidate rules to:")
    print(f"  {output_file}")

def main():
    print("UDCPR Master - LLM Parse Worker")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not set in environment")
        print("Set it in .env file or export OPENAI_API_KEY=your-key")
        return
    
    for pdf_name in PDF_NAMES:
        process_pdf(pdf_name)
    
    print("\n" + "="*60)
    print("✓ LLM parsing complete!")
    print("="*60)
    print("\nNext step: Start admin UI for human verification")
    print("  cd admin_ui && npm start")

if __name__ == "__main__":
    main()
