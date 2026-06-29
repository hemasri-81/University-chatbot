# 🎓 Lexicon – Smart Multilingual AI-Powered Academic Assistant

> **Transforming Academic Learning with Intelligent AI Support**

An AI-powered academic assistant that enables students to interact with educational content using natural language. Leveraging **Retrieval-Augmented Generation (RAG)**, **Large Language Models (LLMs)**, and **Vector Databases**, Lexicon delivers instant, context-aware, multilingual responses from academic documents.

---

## 🚀 Project Overview

Lexicon is an intelligent educational platform designed to simplify the learning experience by allowing students to ask questions naturally and receive accurate answers directly from academic PDFs and study materials.

Instead of searching through hundreds of pages manually, students can interact with an AI assistant that understands context, retrieves relevant information using semantic search, and generates meaningful responses in their preferred language.

The system combines **Generative AI**, **Retrieval-Augmented Generation (RAG)**, **Vector Embeddings**, and **Google Gemini API** to provide personalized, real-time academic assistance.

---


# ✨ Key Features

### 📖 Intelligent Question Answering
Ask questions directly from uploaded academic PDFs.

### 🧠 Context-Aware AI Responses
Uses LLMs to generate accurate and meaningful responses.

### 🌍 Multilingual Support
Supports multiple languages to eliminate learning barriers.

### 🔍 Semantic Search
Uses vector embeddings instead of keyword matching.

### 🤖 Virtual Academic Assistant
Provides instant assistance anytime.

### 📈 Personalized Learning
Tracks learning progress and recommends relevant study materials.

### 📱 User Friendly Interface
Simple and intuitive UI for students and institutions.

---

# 🏗 System Architecture

```
                Academic PDFs
                      │
                      ▼
            PDF Processing & Parsing
                      │
                      ▼
              Text Chunk Generation
                      │
                      ▼
          Sentence Transformer Embeddings
                      │
                      ▼
               Chroma Vector Database
                      │
        Semantic Similarity Search
                      │
                      ▼
              Google Gemini API
                      │
                      ▼
        Context-Aware AI Response
                      │
                      ▼
                 Student Interface
```

---

# 🔄 Website User Flow

### Institution

- Login
- Upload PDFs
- Add Metadata
- Index Documents

↓

### Student

- Login
- Browse Subjects
- Ask Questions
- Select Preferred Language

↓

### AI Processing

- Query Understanding
- Semantic Search
- Context Retrieval
- Response Generation

↓

### Learning

- Follow-up Questions
- Progress Tracking
- Personalized Recommendations
- Adaptive Learning

---

# 🧠 AI Methodology

The chatbot follows a Retrieval-Augmented Generation (RAG) architecture.

### Step 1

User submits a natural language question.

### Step 2

Academic PDFs are converted into chunks.

### Step 3

Chunks are transformed into embeddings using Sentence Transformers.

### Step 4

Embeddings are stored inside ChromaDB.

### Step 5

The system retrieves the most relevant chunks.

### Step 6

Google Gemini receives both:

- User Query
- Retrieved Context

### Step 7

Gemini generates an accurate contextual answer.

---

# 📂 RAG Pipeline

```
PDF Upload
      │
      ▼
Text Extraction
      │
      ▼
Chunking
      │
      ▼
Embeddings
      │
      ▼
Vector Database (ChromaDB)
      │
      ▼
Similarity Search
      │
      ▼
Google Gemini API
      │
      ▼
AI Generated Answer
```

---

# 💻 Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| AI Model | Google Gemini API |
| Framework | LangChain |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers |
| PDF Processing | PyPDF / PDF Processing Libraries |
| Search | Semantic Search |
| Architecture | Retrieval-Augmented Generation (RAG) |

---

# 📁 Suggested Project Structure

```
Lexicon/
│
├── app.py
├── requirements.txt
├── README.md
│
├── backend/
│   ├── api.py
│   ├── rag_pipeline.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── chatbot.py
│
├── frontend/
│   ├── streamlit_app.py
│   ├── pages/
│   └── assets/
│
├── data/
│   ├── pdfs/
│   └── processed/
│
├── chroma_db/
│
├── utils/
│
└── models/
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/lexicon.git
```

Go to project directory

```bash
cd lexicon
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Running the Project

Start backend

```bash
uvicorn backend.api:app --reload
```

Run frontend

```bash
streamlit run frontend/streamlit_app.py
```

---

# 📊 Expected Outcomes

- Faster information retrieval
- Reduced study time
- Better concept understanding
- Personalized learning experience
- Improved accessibility
- Multilingual academic assistance

---

# 🌍 Applications

- Universities
- Colleges
- Schools
- Online Learning Platforms
- Coaching Institutes
- Corporate Training

---

# 🔮 Future Scope

- 🎤 Voice-enabled AI Assistant
- 📝 Handwritten Notes Analysis
- 📱 Android & iOS Application
- 🎯 Personalized AI Learning Paths
- 📚 LMS Integration
- 🧩 Automatic Quiz Generation
- 🌐 Offline AI Support
- 👥 Collaborative Student Forums
- 🌍 Expanded Multilingual Support

---

# 🤝 Contributors

Developed as an AI-powered academic learning platform to enhance educational accessibility using Generative AI and Retrieval-Augmented Generation.

---

# 📜 License

This project is intended for educational and research purposes.

---

# ⭐ If you like this project

Give this repository a ⭐ on GitHub.
