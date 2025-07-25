import re
import sys
import os

def clean_basic_text(text):
    """
    Basic text cleaning - removes extra whitespace and fixes simple formatting
    
    Args:
        text (str): Raw text from PDF extraction
    
    Returns:
        str: Cleaned text
    """
    # Step 1: Handle None or empty text
    if not text or not text.strip():
        return ""
    
    # Step 2: Remove extra whitespace and normalize spaces
    # Replace multiple spaces, tabs, newlines with single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    
    # Step 3: Fix spacing around punctuation
    # Remove space before punctuation
    cleaned_text = re.sub(r'\s+([,.!?;:])', r'\1', cleaned_text)
    # Ensure single space after punctuation
    cleaned_text = re.sub(r'([,.!?;:])\s*', r'\1 ', cleaned_text)
    
    # Step 4: Basic cleanup
    # Remove extra spaces at start and end
    cleaned_text = cleaned_text.strip()
    
    # Step 5: Handle common PDF artifacts
    # Fix broken words (simple cases like "h t" -> "ht")
    cleaned_text = re.sub(r'\b([a-z])\s+([a-z])\b', r'\1\2', cleaned_text)
    
    return cleaned_text


def clean_pdf_artifacts(text):
    """
    Advanced cleaning for PDF extraction artifacts and academic paper issues
    
    Args:
        text (str): Text that has been through basic cleaning
    
    Returns:
        str: Text with PDF artifacts removed
    """
    if not text:
        return ""
    
    cleaned_text = text
    
    # Step 1: Fix broken references and citations
    # Fix spaced references like "[ 1 ]" -> "[1]"
    cleaned_text = re.sub(r'\[\s*(\d+)\s*\]', r'[\1]', cleaned_text)
    # Fix spaced citations like "( Smith et al. , 2020 )" -> "(Smith et al., 2020)"
    cleaned_text = re.sub(r'\(\s*([^)]+?)\s*,\s*(\d{4})\s*\)', r'(\1, \2)', cleaned_text)
    
    # Step 2: Fix mathematical notation and variables
    # Fix spaced variables like "x ∈ R d" -> "x ∈ Rd"
    cleaned_text = re.sub(r'(\w)\s*∈\s*(\w)\s+(\w)', r'\1 ∈ \2\3', cleaned_text)
    # Fix broken subscripts like "h t" -> "h_t" (common in academic papers)
    cleaned_text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s*(?=[,\.\s])', r'\1_\2', cleaned_text)
    
    # Step 3: Fix broken words across line breaks
    # Fix hyphenated words like "atten-tion" -> "attention"
    cleaned_text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', cleaned_text)
    # Fix broken words with spaces like "trans former" -> "transformer"
    cleaned_text = re.sub(r'\b(trans)\s+(former|formation|mit)\b', r'\1\2', cleaned_text)
    cleaned_text = re.sub(r'\b(multi)\s+(head|layer|task)\b', r'\1-\2', cleaned_text)
    cleaned_text = re.sub(r'\b(self)\s+(attention)\b', r'\1-\2', cleaned_text)
    
    # Step 4: Clean up figure and table references
    # Fix spaced figure refs like "Figure 1" -> "Figure 1" (normalize spacing)
    cleaned_text = re.sub(r'(Figure|Fig|Table|Equation)\s*\.?\s*(\d+)', r'\1 \2', cleaned_text)
    # Remove standalone figure/table captions that got mixed in
    cleaned_text = re.sub(r'\b(Figure|Table)\s+\d+[:.].*?(?=\.|$)', '', cleaned_text)
    
    # Step 5: Fix common academic notation
    # Fix degree symbols and mathematical notation
    cleaned_text = re.sub(r'(\d+)\s*°\s*', r'\1° ', cleaned_text)
    # Fix percentage with spaces
    cleaned_text = re.sub(r'(\d+)\s*%', r'\1%', cleaned_text)
    
    # Step 6: Remove extra artifacts
    # Remove multiple periods that come from broken formatting
    cleaned_text = re.sub(r'\.{3,}', '...', cleaned_text)
    # Remove extra commas and fix spacing
    cleaned_text = re.sub(r',\s*,+', ',', cleaned_text)
    
    # Step 7: Final cleanup
    # Remove any leftover multiple spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def clean_academic_text(text):
    """
    Section-specific cleaning for academic papers
    
    Args:
        text (str): Text that has been through basic and artifact cleaning
    
    Returns:
        str: Text optimized for academic content
    """
    if not text:
        return ""
    
    cleaned_text = text
    
    # Step 1: Handle citations and references better
    # Standardize author citations format
    cleaned_text = re.sub(r'\(([A-Z][a-z]+)\s+et\s+al\.\s*,?\s*(\d{4})\)', r'(\1 et al., \2)', cleaned_text)
    
    # Step 2: Fix common academic abbreviations
    # Standardize common abbreviations
    abbreviations = {
        r'\be\.g\.\s*': 'e.g., ',
        r'\bi\.e\.\s*': 'i.e., ',
        r'\bvs\.\s*': 'vs. ',
        r'\betc\.\s*': 'etc. '
    }
    for pattern, replacement in abbreviations.items():
        cleaned_text = re.sub(pattern, replacement, cleaned_text)
    
    # Step 3: Handle section headers that got mixed in
    # Remove standalone section numbers
    cleaned_text = re.sub(r'^\s*\d+\.?\s*$', '', cleaned_text, flags=re.MULTILINE)
    
    # Step 4: Fix equation references
    # Standardize equation references
    cleaned_text = re.sub(r'(Equation|Eq)\s*\.?\s*\((\d+)\)', r'\1 (\2)', cleaned_text)
    
    return cleaned_text


def clean_text_comprehensive(text):
    """
    Apply all cleaning steps in the right order
    
    Args:
        text (str): Raw text from PDF extraction
    
    Returns:
        str: Fully cleaned text ready for processing
    """
    # Apply cleaning in order
    cleaned = clean_basic_text(text)
    cleaned = clean_pdf_artifacts(cleaned)
    cleaned = clean_academic_text(cleaned)
    
    return cleaned


def test_advanced_cleaning():
    """
    Test the advanced cleaning functions
    """
    # Sample problematic text with various issues
    sample_text = """Recurrent neural networks, long short-term memory  [ 1 ] and gated recurrent units ( Cho et al. , 2014 ) have been used for trans former architecture. The multi head attention mechanism in Figure 1 shows h t variables. We see that x ∈ R d represents the input. This is simi-lar to previous work... The self attention mechanism performs better than tra-ditional approaches."""
    
    print("=== ADVANCED CLEANING TEST ===")
    print(f"Original text:\n{sample_text}")
    print(f"\nLength: {len(sample_text)} characters")
    
    # Apply comprehensive cleaning
    cleaned = clean_text_comprehensive(sample_text)
    
    print(f"\nCleaned text:\n{cleaned}")
    print(f"\nLength: {len(cleaned)} characters")
    print(f"Difference: {len(sample_text) - len(cleaned)} characters removed")


def test_basic_cleaning():
    """
    Test function to see how the cleaning works with sample text
    """
    # Sample text from your actual extraction (with problems)
    sample_text = "Recurrent neural networks, long short-term memory  Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states h t , as a function of the previous hidden sta a..."
    
    print("=== BASIC TEXT CLEANING TEST ===")
    print(f"Original text:\n{sample_text}")
    print(f"\nLength: {len(sample_text)} characters")
    
    # Apply cleaning
    cleaned = clean_basic_text(sample_text)
    
    print(f"\nCleaned text:\n{cleaned}")
    print(f"\nLength: {len(cleaned)} characters")
    print(f"Difference: {len(sample_text) - len(cleaned)} characters removed")


def test_with_real_data():
    """
    Test with actual data from parse_pdf.py
    """
    # Import your parser
    sys.path.append(os.path.dirname(__file__))
    try:
        from parse_pdf import parse_pdf_with_grobid
        
        print("=== TESTING WITH REAL DATA ===")
        pdf_path = "papers/attention_is_all_you_need.pdf"
        output_dir = "output"
        
        # Get the parsed data
        result = parse_pdf_with_grobid(pdf_path, output_dir)
        
        # Test cleaning on one section
        section_name = "Introduction"
        if section_name in result['sections']:
            original_text = result['sections'][section_name]
            basic_cleaned = clean_basic_text(original_text)
            comprehensive_cleaned = clean_text_comprehensive(original_text)
            
            print(f"Section: {section_name}")
            print(f"Original length: {len(original_text)} characters")
            print(f"Basic cleaned length: {len(basic_cleaned)} characters")
            print(f"Comprehensive cleaned length: {len(comprehensive_cleaned)} characters")
            print(f"Total reduction: {len(original_text) - len(comprehensive_cleaned)} characters")
            print(f"\nFirst 200 characters of comprehensive cleaned text:")
            print(f"{comprehensive_cleaned[:200]}...")
        else:
            print(f"Section '{section_name}' not found")
            print(f"Available sections: {list(result['sections'].keys())}")
            
    except Exception as e:
        print(f"Error testing with real data: {e}")
        print("Make sure GROBID is running and parse_pdf.py works")


if __name__ == "__main__":
    # Run tests
    print("Step 1: Basic cleaning test")
    test_basic_cleaning()
    print("\n" + "="*50 + "\n")
    
    print("Step 2: Advanced cleaning test")
    test_advanced_cleaning()
    print("\n" + "="*50 + "\n")
    
    print("Step 3: Real data with comprehensive cleaning")
    test_with_real_data()
