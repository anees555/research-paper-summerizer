#!/usr/bin/env python3
"""
PDF parser using direct GROBID HTTP API calls instead of grobid-client-python
This bypasses issues with the client library and processes PDFs directly.
"""

import os
import xml.etree.ElementTree as ET
import requests
import logging
import sys
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_pdf_with_grobid(pdf_path, output_dir):
    """
    Parse a PDF using direct GROBID HTTP API calls to extract metadata and sections.
    """
    try:
        # Check GROBID server health
        max_retries = 3
        retry_delay = 10
        for attempt in range(max_retries):
            try:
                response = requests.get("http://localhost:8070/api/isalive", timeout=10)
                if response.status_code == 200 and "true" in response.text.lower():
                    logger.info("✅ GROBID server is reachable and alive")
                    break
                else:
                    logger.warning(f"GROBID server returned unexpected response: {response.text.strip()}")
                    time.sleep(retry_delay)
            except requests.ConnectionError:
                logger.warning(f"⚠️ GROBID server not reachable (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
        else:
            logger.error("❌ GROBID server is not reachable after retries")
            raise ConnectionError("GROBID server is not reachable")

        # Validate input PDF
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not pdf_path.endswith('.pdf'):
            logger.error(f"Invalid file format: {pdf_path}. Must be a PDF.")
            raise ValueError("Input file must be a PDF.")

        logger.info(f"📄 Processing PDF: {pdf_path}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Process PDF with direct GROBID API call
        url = "http://localhost:8070/api/processFulltextDocument"
        
        with open(pdf_path, 'rb') as f:
            files = {'input': f}
            data = {
                'consolidateHeader': '1',
                'consolidateCitations': '1'
            }
            
            logger.info("🚀 Sending PDF to GROBID for processing...")
            response = requests.post(url, files=files, data=data, timeout=180)
            
        if response.status_code != 200:
            logger.error(f"GROBID processing failed with status {response.status_code}")
            logger.error(f"Response: {response.text[:500]}...")
            raise Exception(f"GROBID processing failed: {response.status_code}")
            
        # Save TEI XML output
        pdf_name = os.path.basename(pdf_path).replace(".pdf", "")
        output_file = os.path.join(output_dir, f"{pdf_name}.tei.xml")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        logger.info(f"💾 Saved TEI XML to: {output_file}")
        logger.info(f"📊 TEI XML size: {len(response.text):,} characters")

        # Parse TEI XML
        logger.info(f"📑 Parsing TEI XML...")
        root = ET.fromstring(response.text)

        # Define TEI namespace
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}

        # Extract metadata
        title_elem = root.find(".//tei:titleStmt/tei:title", ns)
        title = title_elem.text if title_elem is not None else "Unknown Title"
        
        authors = []
        for author in root.findall(".//tei:author", ns):
            forename = author.find(".//tei:forename", ns)
            surname = author.find(".//tei:surname", ns)
            author_name = (f"{forename.text} {surname.text}" 
                          if forename is not None and surname is not None 
                          else "Unknown Author")
            authors.append(author_name)

        abstract_elem = root.find(".//tei:abstract/tei:div/tei:p", ns)
        abstract = abstract_elem.text if abstract_elem is not None else ""

        # Extract sections
        sections = {}
        for div in root.findall(".//tei:body/tei:div", ns):
            head = div.find("tei:head", ns)
            section_title = head.text if head is not None else "Untitled"
            
            # Get all text content from the section
            section_text = ""
            for elem in div.iter():
                if elem.text:
                    section_text += elem.text.strip() + " "
                if elem.tail:
                    section_text += elem.tail.strip() + " "
            
            sections[section_title] = section_text.strip()

        logger.info(f"📋 Extracted {len(sections)} sections")
        
        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "sections": sections,
            "tei_xml_path": output_file
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise

def print_available_pdfs():
    """Print available PDFs in the papers directory"""
    papers_dir = "papers"
    if os.path.exists(papers_dir):
        pdfs = [f for f in os.listdir(papers_dir) if f.endswith('.pdf')]
        if pdfs:
            print("Available PDFs in papers/:")
            for pdf in pdfs:
                print(f"  - {pdf}")
        else:
            print("No PDFs found in papers/ directory")
    else:
        print("papers/ directory not found")

def main():
    """Main function to process a PDF or show usage"""
    if len(sys.argv) != 2:
        print("Usage: python parse_pdf_direct.py <path_to_pdf>")
        print_available_pdfs()
        return

    pdf_path = sys.argv[1]
    output_dir = "output"
    
    try:
        result = parse_pdf_with_grobid(pdf_path, output_dir)
        
        print("\n" + "="*50)
        print("📄 PDF PARSING COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"📖 Title: {result['title']}")
        print(f"✍️  Authors: {', '.join(result['authors']) if result['authors'] else 'None'}")
        print(f"📝 Abstract: {result['abstract'][:200]}{'...' if len(result['abstract']) > 200 else ''}")
        print(f"📋 Sections found: {len(result['sections'])}")
        
        for i, section_title in enumerate(list(result['sections'].keys())[:5], 1):
            section_preview = result['sections'][section_title][:100]
            print(f"  {i}. {section_title}: {section_preview}{'...' if len(result['sections'][section_title]) > 100 else ''}")
        
        if len(result['sections']) > 5:
            print(f"  ... and {len(result['sections']) - 5} more sections")
            
        print(f"💾 TEI XML saved to: {result['tei_xml_path']}")
        print("\n✅ Ready for text preprocessing and summarization!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print_available_pdfs()

if __name__ == "__main__":
    main()
