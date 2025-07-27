# AI-Powered Research Paper Analysis Platform

🚀 **An intelligent web application that transforms how researchers interact with scientific literature**

## 📋 **Overview**

This project is a comprehensive **AI-powered web application** that enables users to upload research papers in PDF format and receive:
- **Multi-level textual summaries** (1-line, bullet-point, paragraph, deep analysis)
- **Extracted visual insights** (figures, tables, mathematical formulas)  
- **Contribution flow visualization** (Problem → Method → Results → Conclusion)
- **Intelligent analysis** (domain classification, quality assessment, impact prediction)

**Goal**: Reduce reading time by up to **80%** and make scientific content more accessible.

## 🏗️ **Technology Stack**

- **Frontend**: React (Interactive UI, real-time updates)
- **Backend**: FastAPI + Celery (High-performance API, background processing)
- **Database**: PostgreSQL (Structured data storage)
- **AI Models**: BART, Longformer, BERT (Multi-model analysis)
- **Processing**: GROBID, pdfplumber, Mathpix/Pix2Text (Content extraction)
- **Visualization**: Mermaid.js (Contribution flow charts)

## ⚡ **Key Features**

### 🎯 **Multi-Level Summarization**
- **1-Line**: Essential finding in one sentence
- **Bullet Points**: Key contributions and findings  
- **Paragraph**: Structured abstract-style summary
- **Deep Analysis**: Comprehensive multi-paragraph analysis

### 🔍 **Visual Content Extraction**
- Mathematical formulas with LaTeX rendering
- High-quality figures and tables
- Automated chart descriptions

### 📊 **Contribution Flow Visualization**  
- Interactive Problem → Method → Results → Conclusion flow
- LLM-generated logical connections
- Mermaid.js rendered diagrams

### 🧠 **Intelligent Analysis**
- Domain classification and quality assessment
- Citation prediction and impact estimation
- Related work recommendations

## 🚀 **Current Status**

- ✅ **PDF Processing Pipeline**: GROBID integration, text preprocessing, chunking
- ✅ **AI Model Integration**: BART and Longformer ready for inference
- ✅ **Core Infrastructure**: Reliable PDF parsing, multi-model text processing
- 🔄 **In Progress**: FastAPI backend, visual extraction, frontend development

## 📁 **Project Structure**

```
research_summary_project/
├── scripts/
│   ├── parse_pdf.py          # PDF processing with GROBID
│   ├── preprocess_text.py    # Text cleaning and chunking
│   └── process_and_summerize.py # Main processing pipeline
├── papers/                   # Input PDF files
├── output/                   # Processed results (TEI XML, etc.)
├── config.json              # GROBID configuration
└── requirements.txt         # Python dependencies
```

## 🛠️ **Setup Instructions**

### Prerequisites
- Python 3.9+
- Docker (for GROBID)
- PostgreSQL (for production)

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/anees555/research-paper-summerizer.git
   cd research-paper-summerizer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start GROBID Docker container**
   ```bash
   docker run -d --name grobid -p 8070:8070 lfoppiano/grobid:0.8.0
   ```

5. **Test the pipeline**
   ```bash
   python test_pipeline.py
   ```

## 📖 **Usage**

### Basic PDF Processing
```python
from scripts.parse_pdf import parse_pdf_with_grobid
from scripts.preprocess_text import prepare_paper_for_summarization

# Process a PDF
result = parse_pdf_with_grobid("papers/example.pdf", "output")
print(f"Extracted {len(result['sections'])} sections")

# Prepare for AI models
processed = prepare_paper_for_summarization(result)
print(f"BART chunks: {len(processed['bart_chunks'])}")
print(f"Longformer chunks: {len(processed['longformer_chunks'])}")
```

### Complete Pipeline Test
```bash
python test_pipeline.py papers/attention_is_all_you_need.pdf
```

## 🎯 **Roadmap**

- [ ] **FastAPI Backend** (Weeks 1-2)
- [ ] **AI Model Serving** (Weeks 3-4)  
- [ ] **Visual Processing** (Weeks 5-6)
- [ ] **React Frontend** (Weeks 7-8)
- [ ] **Production Deployment** (Weeks 9-10)

## 📊 **Expected Impact**

- **80% reduction** in paper reading time
- **Faster literature reviews** for researchers  
- **Improved accessibility** of scientific content
- **Enhanced research productivity** across domains

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 **Authors**

- **Anish Dahal** - *Initial work* - [GitHub](https://github.com/anees555)

## 🙏 **Acknowledgments**

- GROBID team for document processing
- Hugging Face for transformer models
- Open source community for tools and libraries