import os
import xml.etree.ElementTree as ET
from grobid_client.grobid_client import GrobidClient
import logging
import sys
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_pdf_with_grobid(pdf_path, output_dir):
    """
    Parse a PDF using GROBID to extract metadata and sections, saving TEI XML to output_dir.
    """
    try:
        # Check GROBID server with retries using proper health endpoint
        max_retries = 3
        retry_delay = 10  # seconds
        for attempt in range(max_retries):
            try:
                response = requests.get("http://localhost:8070/api/isalive", timeout=10)
                if response.status_code == 200 and "true" in response.text.lower():
                    logger.info("✅ GROBID server is reachable and alive")
                    break
                else:
                    logger.warning(f"GROBID server returned unexpected response: {response.text.strip()}, retrying...")
                    time.sleep(retry_delay)
            except requests.ConnectionError:
                logger.warning(f"⚠️ GROBID server not reachable (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(retry_delay)
        else:
            logger.error("❌ GROBID server is not reachable after retries")
            raise ConnectionError("GROBID server is not reachable at http://localhost:8070/api/isalive")

        # Normalize paths
        pdf_path = os.path.normpath(pdf_path)
        output_dir = os.path.normpath(output_dir)
        
        # Validate input PDF
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not pdf_path.endswith('.pdf'):
            logger.error(f"Invalid file format: {pdf_path}. Must be a PDF.")
            raise ValueError("Input file must be a PDF.")

        # Initialize GROBID client
        client = GrobidClient(config_path="config.json")
        logger.info(f"📄 Processing PDF: {pdf_path}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Process PDF with GROBID
        client.process(
            service="processFulltextDocument",
            input_path=os.path.dirname(pdf_path),
            output=output_dir,
            consolidate_header=True,
            consolidate_citations=True,
            force=True
)

        # Construct path to TEI XML output
        output_file = os.path.join(output_dir, os.path.basename(pdf_path).replace(".pdf", ".tei.xml"))
        if not os.path.exists(output_file):
            logger.error(f"GROBID failed to generate TEI XML: {output_file}")
            raise FileNotFoundError(f"TEI XML output not found: {output_file}")

        # Parse TEI XML
        logger.info(f"📑 Parsing TEI XML: {output_file}")
        tree = ET.parse(output_file)
        root = tree.getroot()

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
            section_text = " ".join([p.text for p in div.findall("tei:p", ns) if p.text])
            if section_text:
                sections[section_title] = section_text

        logger.info("✅ Extraction successful")
        return {
            "metadata": {
                "title": title,
                "authors": authors,
                "abstract": abstract
            },
            "sections": sections
        }

    except ET.ParseError as e:
        logger.error(f"Failed to parse TEI XML: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise

if __name__ == "__main__":
    output_dir = "output"
    
    if len(sys.argv) > 1:
        provided_path = sys.argv[1]
        if not os.path.dirname(provided_path):
            pdf_path = os.path.join("papers", provided_path)
        else:
            pdf_path = provided_path
    else:
        pdf_path = os.path.join("papers", "attention_is_all_you_need.pdf")
    
    try:
        result = parse_pdf_with_grobid(pdf_path, output_dir)
        print("\n📄 Metadata:")
        print(f"Title: {result['metadata']['title']}")
        print(f"Authors: {', '.join(result['metadata']['authors'])}")
        print(f"Abstract: {result['metadata']['abstract']}\n")

        print("📚 Sections:")
        for title, text in result['sections'].items():
            print(f"\n🔹 {title}:\n{text[:300]}...")  # Truncate for readability
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Available PDFs in papers/:")
        try:
            print(os.listdir("papers"))
        except Exception as e:
            print(f"Could not list files in 'papers/': {e}")
