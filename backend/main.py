"""
Smart Multilingual AI-Powered Academic Assistant
Phase 1 MVP: RAG-based PDF chatbot for academic materials
With OCR support for image-based PDFs and PDF file retrieval
"""
import os

# Disable Chroma telemetry logs
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Hide warnings
import warnings
warnings.filterwarnings("ignore")

import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime

from dotenv import load_dotenv

# Add parent directory to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

# LangChain Imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.schema import Document

# OCR imports for image-based PDFs
import pytesseract
from pdf2image import convert_from_path

# ========== IMPORTANT: Configure Tesseract Path ==========
# Set the path to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# =========================================================

# ========== Configure Poppler Path ==========
# Set the path to poppler bin folder (update this to your actual path)
# Option 1: If poppler is in your project folder
POPPLER_PATH = project_root / "poppler" / "Library" / "bin"
if not POPPLER_PATH.exists():
    # Option 2: If poppler is installed in Program Files
    POPPLER_PATH = Path(r'C:\Program Files\poppler\Library\bin')
    if not POPPLER_PATH.exists():
        # Option 3: Try common alternative location
        POPPLER_PATH = Path(r'C:\poppler\bin')
        if not POPPLER_PATH.exists():
            POPPLER_PATH = None
            print("⚠️ Poppler not found. Install from: https://github.com/oschwartz10612/poppler-windows/releases/")
        else:
            print(f"✅ Poppler found at: {POPPLER_PATH}")
    else:
        print(f"✅ Poppler found at: {POPPLER_PATH}")
else:
    print(f"✅ Poppler found at: {POPPLER_PATH}")
# =========================================================

import chromadb 
chromadb.api.client.SharedSystemClient.clear_system_cache()


class PDFProcessor:
    """
    Enhanced PDF processor with OCR support for image-based PDFs
    """
    
    @staticmethod
    def is_scanned_pdf(pdf_path: str, sample_pages: int = 2) -> bool:
        """
        Check if PDF is scanned/image-based by trying to extract text
        """
        try:
            # Try normal text extraction first
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            
            # Check if extracted text has meaningful content
            total_text = " ".join([doc.page_content for doc in docs[:sample_pages]])
            
            # If extracted text is too short or mostly whitespace, it's likely scanned
            if len(total_text.strip()) < 100:  # Arbitrary threshold
                return True
            return False
        except:
            return True
    
    @staticmethod
    def extract_text_with_ocr(pdf_path: str, dpi: int = 300) -> List[Document]:
        """
        Extract text from image-based PDF using OCR
        """
        print(f"🔍 Using OCR for scanned PDF: {os.path.basename(pdf_path)}")
        
        documents = []
        
        try:
            # Convert PDF pages to images
            print(f"📄 Converting PDF pages to images...")
            
            # Use the globally defined POPPLER_PATH
            images = None
            if POPPLER_PATH and POPPLER_PATH.exists():
                try:
                    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=str(POPPLER_PATH))
                    print(f"   Using poppler from: {POPPLER_PATH}")
                except Exception as e:
                    print(f"   Error with specified poppler path: {e}")
                    # Fallback to default
                    images = convert_from_path(pdf_path, dpi=dpi)
            else:
                # Try without specifying poppler path (relies on system PATH)
                images = convert_from_path(pdf_path, dpi=dpi)
            
            if not images:
                raise Exception("Could not convert PDF to images. Please install poppler.")
            
            print(f"   Processing {len(images)} pages...")
            
            for page_num, image in enumerate(images, start=1):
                print(f"  • Page {page_num}/{len(images)}")
                
                # Extract text from image using Tesseract
                # Configure Tesseract for better accuracy
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(image, config=custom_config)
                
                if text.strip():
                    # Create document with metadata
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": Path(pdf_path).name,
                            "page": page_num,
                            "ocr_processed": True
                        }
                    )
                    documents.append(doc)
                    print(f"     ✅ Extracted {len(text)} characters")
                else:
                    print(f"     ⚠️ No text found on page {page_num}")
                    
        except Exception as e:
            print(f"❌ OCR Error for {pdf_path}: {e}")
            print(f"   Make sure Poppler is installed: https://github.com/oschwartz10612/poppler-windows/releases/")
            # Fallback to regular PDF loading
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            print(f"   ⚠️ Falling back to standard PDF extraction")
            
        return documents
    
    @staticmethod
    def load_pdf_with_ocr_fallback(pdf_path: str) -> List[Document]:
        """
        Load PDF with automatic fallback to OCR if needed
        """
        print(f"• Loading: {Path(pdf_path).name}")
        
        # Check if PDF is scanned
        if PDFProcessor.is_scanned_pdf(pdf_path):
            print(f"  📸 Detected as image-based PDF, using OCR...")
            documents = PDFProcessor.extract_text_with_ocr(pdf_path)
        else:
            print(f"  📝 Detected as text-based PDF, using normal extraction...")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            print(f"     ✅ Loaded {len(documents)} pages")
            
        return documents


class AcademicAssistant:
    """
    Main Academic Assistant Class with PDF retrieval capability
    """

    def __init__(self):

        # API Key
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.gemini_api_key:
            print("⚠️ Warning: GOOGLE_API_KEY not found in .env file")
            print("   Please create a .env file with: GOOGLE_API_KEY=your_key_here")

        # Models
        self.model_name = os.getenv(
            "MODEL_NAME",
            "gemini-1.5-flash"
        )

        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL_NAME",
            "all-MiniLM-L6-v2"
        )

        # Chunk settings
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))

        # Paths
        self.study_materials_dir = project_root / "study_materials"
        self.vector_db_dir = project_root / "vector_db"
        self.pdf_export_dir = project_root / "exported_pdfs"

        # Components
        self.vector_store = None
        self.qa_chain = None

        # Create folders if not exist
        self.study_materials_dir.mkdir(exist_ok=True)
        self.vector_db_dir.mkdir(exist_ok=True)
        self.pdf_export_dir.mkdir(exist_ok=True)
        
        # Store available PDFs
        self.available_pdfs = {}

    def load_pdfs(self) -> List[Any]:
        """
        Load PDFs from study_materials folder with OCR support
        """
        print("\n📚 Loading PDFs with OCR support...")
        print("-" * 40)
        
        documents = []
        
        print(f"Study Material Path: {self.study_materials_dir}")
        
        # List all files in the directory
        all_files = os.listdir(self.study_materials_dir)
        print(f"Available Files: {all_files}")
        
        pdf_files = [
            file for file in self.study_materials_dir.iterdir()
            if file.is_file() and file.suffix.lower() == ".pdf"
        ]
        
        if not pdf_files:
            raise FileNotFoundError(
                f"\n❌ No PDFs found in {self.study_materials_dir}\n"
                f"Please add PDF files to this folder and restart the assistant."
            )
            
        print(f"\nFound {len(pdf_files)} PDF(s):")
        
        for pdf_path in pdf_files:
            # Store PDF path for retrieval
            self.available_pdfs[pdf_path.name.lower()] = pdf_path
            
            # Load PDF with OCR fallback
            pdf_docs = PDFProcessor.load_pdf_with_ocr_fallback(str(pdf_path))
            
            # Add metadata
            for doc in pdf_docs:
                doc.metadata["source"] = pdf_path.name
                doc.metadata["pdf_path"] = str(pdf_path)
                
            documents.extend(pdf_docs)
            
        print(f"\n✅ Loaded {len(documents)} total pages from {len(pdf_files)} PDFs")
        print(f"📄 Available PDFs: {', '.join(self.available_pdfs.keys())}")
        print("-" * 40)
        
        return documents

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        """
        Split documents into chunks
        """
        print("\n✂️ Splitting documents into chunks...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        return chunks

    def create_embeddings(self, chunks: List[Any]):
        """
        Create embeddings and store in ChromaDB
        """
        print("\n🔢 Creating embeddings...")
        print("   This may take a moment depending on the number of chunks...")
        
        embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        print("📦 Storing embeddings in ChromaDB...")
        
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(self.vector_db_dir),
            collection_name="academic_materials"
        )
        
        print("✅ Vector database created successfully")

    def initialize_qa_chain(self):
        """
        Initialize Gemini QA chain
        """
        print("\n🤖 Initializing Gemini model...")
        
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please check your .env file")
        
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.gemini_api_key,
                temperature=0.1,
                convert_system_message_to_human=True
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 4}
                ),
                return_source_documents=True
            )
            
            print(f"✅ QA chain initialized with model: {self.model_name}")
        except Exception as e:
            print(f"❌ Failed to initialize QA chain: {e}")
            print("Please check your GOOGLE_API_KEY in .env file")
            raise

    def is_pdf_request(self, question: str) -> tuple:
        """
        Check if user is requesting a PDF file
        Returns (is_request, pdf_name)
        """
        question_lower = question.lower()
        
        # Patterns for PDF requests
        patterns = [
            r'(?:provide|get|give|show|send|share|download)\s+(?:me\s+)?(?:the\s+)?([\w\s]+?)\s+pdf',
            r'(?:where\s+is\s+)?([\w\s]+?)\s+pdf',
            r'pdf\s+(?:named\s+)?([\w\s]+)',
            r'(?:get|show)\s+([\w\s]+?)\s+document',
            r'provide\s+([\w\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question_lower)
            if match:
                requested_name = match.group(1).strip()
                # Find matching PDF
                for pdf_name in self.available_pdfs.keys():
                    if requested_name in pdf_name or pdf_name.startswith(requested_name):
                        return True, pdf_name
                        
        return False, None

    def retrieve_pdf(self, pdf_name: str) -> Dict[str, Any]:
        """
        Retrieve and return the requested PDF
        """
        # Find matching PDF
        matching_pdfs = []
        for available_name, pdf_path in self.available_pdfs.items():
            if pdf_name.lower() in available_name or available_name.startswith(pdf_name.lower()):
                matching_pdfs.append((available_name, pdf_path))
        
        if not matching_pdfs:
            return {
                "success": False,
                "message": f"PDF '{pdf_name}' not found. Available PDFs: {', '.join(self.available_pdfs.keys())}"
            }
        
        if len(matching_pdfs) > 1:
            return {
                "success": False,
                "message": f"Multiple PDFs found matching '{pdf_name}'. Please be more specific: {', '.join([m[0] for m in matching_pdfs])}"
            }
        
        pdf_name_match, pdf_path = matching_pdfs[0]
        
        # Copy PDF to export directory for serving
        export_path = self.pdf_export_dir / pdf_path.name
        shutil.copy2(pdf_path, export_path)
        
        return {
            "success": True,
            "message": f"Found PDF: {pdf_name_match}",
            "pdf_path": str(export_path),
            "pdf_name": pdf_name_match,
            "file_size": f"{pdf_path.stat().st_size / 1024:.2f} KB"
        }

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer user question with PDF retrieval capability
        """
        # First, check if user is requesting a PDF
        is_pdf_req, pdf_name = self.is_pdf_request(question)
        
        if is_pdf_req:
            print(f"\n📄 PDF Request detected")
            result = self.retrieve_pdf(pdf_name)
            return {
                "question": question,
                "is_pdf_request": True,
                "pdf_result": result,
                "answer": result["message"],
                "sources": [],
                "context_chunks": 0
            }
        
        # Normal Q&A
        if not self.qa_chain:
            raise ValueError("QA Chain not initialized")
            
        print(f"\n🧠 Processing question...")
        
        try:
            result = self.qa_chain.invoke({"query": question})
            
            # Get sources
            source_pdfs = set()
            for doc in result["source_documents"]:
                if "source" in doc.metadata:
                    source_pdfs.add(doc.metadata["source"])
            
            return {
                "question": question,
                "is_pdf_request": False,
                "answer": result["result"],
                "sources": list(source_pdfs),
                "context_chunks": len(result["source_documents"]),
                "pdf_result": None
            }
        except Exception as e:
            return {
                "question": question,
                "is_pdf_request": False,
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "sources": [],
                "context_chunks": 0,
                "pdf_result": None,
                "error": str(e)
            }

    def setup(self):
        """
        Setup complete pipeline
        """
        print("=" * 60)
        print("🤖 ACADEMIC ASSISTANT SETUP")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
        print(f"⏰ Time: {datetime.now().strftime('%I:%M %p')}")
        print("=" * 60)
        
        # Check OCR availability
        print("\n🔍 Checking OCR Configuration...")
        try:
            tesseract_version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR: {tesseract_version}")
        except Exception as e:
            print(f"⚠️ Tesseract OCR issue: {e}")
            print("   Install from: https://github.com/UB-Mannheim/tesseract/releases")
        
        if POPPLER_PATH and POPPLER_PATH.exists():
            print(f"✅ Poppler: Found at {POPPLER_PATH}")
        else:
            print(f"⚠️ Poppler: Not found. OCR for image PDFs may fail")
            print("   Install from: https://github.com/oschwartz10612/poppler-windows/releases/")
        
        print("\n" + "=" * 60)
        print("📚 PROCESSING DOCUMENTS")
        print("=" * 60)
        
        # Step 1: Load PDFs with OCR
        documents = self.load_pdfs()
        
        # Step 2: Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Step 3: Create embeddings
        self.create_embeddings(chunks)
        
        # Step 4: Initialize QA chain
        self.initialize_qa_chain()
        
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        print("\n💡 FEATURES:")
        print("  • Ask questions about your PDF content")
        print("  • Request PDFs: 'provide me [name] pdf'")
        print("  • OCR support for scanned documents and images")
        print("=" * 60)

    def interactive_mode(self):
        """
        Start chatbot interaction
        """
        print("\n💬 INTERACTIVE MODE")
        print("Type 'exit' to quit, 'help' for examples")
        print("-" * 60)
        
        while True:
            try:
                question = input("\n📝 You: ").strip()
                
                if question.lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Goodbye! Have a great day!")
                    break
                
                if question.lower() == "help":
                    print("\n📖 EXAMPLE QUESTIONS:")
                    print("  • What is lexical analysis?")
                    print("  • Explain tokens in compiler design")
                    print("  • Provide me the CD pdf")
                    print("  • Show me the timetable document")
                    print("  • What are the key concepts in chapter 1?")
                    continue
                
                if not question:
                    print("⚠️ Please enter a question")
                    continue
                
                # Get answer/PDF
                result = self.answer_question(question)
                
                # Handle PDF request response
                if result.get("is_pdf_request"):
                    print("\n" + "=" * 60)
                    print("📄 PDF RETRIEVAL")
                    print("=" * 60)
                    
                    pdf_result = result["pdf_result"]
                    if pdf_result["success"]:
                        print(f"✅ {pdf_result['message']}")
                        print(f"📁 File: {pdf_result['pdf_name']}")
                        print(f"📏 Size: {pdf_result['file_size']}")
                        print(f"📂 Location: {pdf_result['pdf_path']}")
                        print("\n💡 You can find the PDF in the 'exported_pdfs' folder")
                    else:
                        print(f"❌ {pdf_result['message']}")
                    
                    print("=" * 60)
                else:
                    # Normal Q&A response
                    print("\n" + "=" * 60)
                    print("💡 ANSWER")
                    print("=" * 60)
                    print(result["answer"])
                    
                    if result.get("sources"):
                        print("\n" + "-" * 40)
                        print("📚 SOURCES:")
                        for source in result["sources"]:
                            print(f"  • {source}")
                        print(f"\n  Retrieved from {result['context_chunks']} chunks")
                    
                    print("=" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue


def main():
    try:
        print("\n" + "=" * 60)
        print("🚀 STARTING ACADEMIC ASSISTANT")
        print("=" * 60)
        
        # Verify Tesseract is configured
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR Version: {version}")
        except Exception as e:
            print(f"⚠️ Tesseract not properly configured: {e}")
            print("   OCR for images will not work properly.")
            print("   Install from: https://github.com/UB-Mannheim/tesseract/releases")
        
        assistant = AcademicAssistant()
        assistant.setup()
        assistant.interactive_mode()
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())