#!/usr/bin/env python3
"""
Test the complete pipeline: PDF parsing → preprocessing → chunking
"""

from scripts.parse_pdf import parse_pdf_with_grobid
from scripts.preprocess_text import clean_text_comprehensive, chunk_text_for_models

def test_complete_pipeline(pdf_path):
    """Test the complete pipeline with a PDF"""
    print(f"🧪 Testing complete pipeline with: {pdf_path}")
    print("="*60)
    
    # Step 1: Parse PDF
    print("📄 Step 1: Parsing PDF with GROBID...")
    paper_data = parse_pdf_with_grobid(pdf_path, "output")
    
    # Step 2: Test preprocessing and chunking
    print(f"\n📝 Step 2: Processing {len(paper_data['sections'])} sections...")
    
    bart_chunks = []
    longformer_chunks = []
    
    # Process each section
    for section_name, section_text in paper_data['sections'].items():
        print(f"\n📋 Processing section: {section_name}")
        print(f"   Original length: {len(section_text)} characters")
        
        # Clean the text
        cleaned_text = clean_text_comprehensive(section_text)
        print(f"   Cleaned length: {len(cleaned_text)} characters")
        
        # Create BART chunks (for one-line summaries)
        bart_section_chunks = chunk_text_for_models(cleaned_text, "bart")
        for chunk in bart_section_chunks:
            chunk["section_name"] = section_name
        bart_chunks.extend(bart_section_chunks)
        
        # Create Longformer chunks (for deep summaries)
        longformer_section_chunks = chunk_text_for_models(cleaned_text, "longformer")
        for chunk in longformer_section_chunks:
            chunk["section_name"] = section_name
        longformer_chunks.extend(longformer_section_chunks)
        
        print(f"   BART chunks: {len(bart_section_chunks)}")
        print(f"   Longformer chunks: {len(longformer_section_chunks)}")
    
    # Step 3: Summary
    print(f"\n✅ Pipeline Complete!")
    print("="*60)
    print(f"📖 Title: {paper_data['title']}")
    print(f"✍️  Authors: {len(paper_data['authors'])} authors")
    print(f"📝 Abstract: {len(paper_data['abstract'])} characters")
    print(f"📋 Sections: {len(paper_data['sections'])}")
    print(f"🎯 BART chunks (for one-line summaries): {len(bart_chunks)}")
    print(f"🔍 Longformer chunks (for deep summaries): {len(longformer_chunks)}")
    
    # Show sample chunks
    if bart_chunks:
        print(f"\n🎯 Sample BART chunk (from {bart_chunks[0]['section_name']}):")
        print(f"   Words: {bart_chunks[0]['word_count']}")
        print(f"   Preview: {bart_chunks[0]['text'][:200]}...")
        
    if longformer_chunks:
        print(f"\n🔍 Sample Longformer chunk (from {longformer_chunks[0]['section_name']}):")
        print(f"   Words: {longformer_chunks[0]['word_count']}")
        print(f"   Preview: {longformer_chunks[0]['text'][:200]}...")
    
    return {
        "paper_data": paper_data,
        "bart_chunks": bart_chunks,
        "longformer_chunks": longformer_chunks
    }

if __name__ == "__main__":
    # Test with the new PDF
    result = test_complete_pipeline("papers/Manimator_Transforming_Research_Papers_into_Visual.pdf")
