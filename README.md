# AMTManApp ✈️🛠

**AMTManApp (Aircraft Maintenance Technician Manual App)** is an AI-powered assistant designed to help aircraft maintenance professionals query, analyze, and retrieve information from Aircraft Maintenance Manuals (AMMs).

It combines **Retrieval-Augmented Generation (RAG)**, **LangChain / LangGraph agents**, and **PDF document processing** to provide accurate, task-focused maintenance guidance.

---

## 🚀 Key Features

- 📚 **PDF-based RAG**
  - Loads multiple AMM PDFs
  - Splits, embeds, and stores content in a vector database
  - Retrieves relevant manual sections based on user queries

- 🧠 **Agent-driven task routing**
  - Routes user queries to specialized tools:
    - Symptom diagnosis
    - Maintenance task discovery
    - PDF file retrieval by task number
  - Enforces strict stop conditions to avoid hallucinations or loops

- 🧾 **Maintenance task extraction**
  - Extracts ATA task numbers and descriptions
  - Supports multiple ATA chapters and systems
  - Regex-based task number detection

- 🔗 **PDF link extraction**
  - Detects embedded links to other PDFs inside manuals
  - Supports `/F` (file) links commonly found in AMMs

- 💬 **Conversation history**
  - Stores Human ↔ AI interactions in a database
  - User-based history retrieval
  - Streamlit sidebar for browsing past sessions

- 🖥 **Streamlit UI**
  - Interactive web interface
  - Sidebar user selection
  - Offline-safe behavior when LLM is unavailable

---

## 🧩 Architecture Overview

PDF Manuals
↓
Document Loaders (PyPDFLoader)
↓
Text Splitter
↓
Embeddings (OpenAI)
↓
Vector Store (FAISS)
↓
Retriever
↓
LangGraph Agent
↓
Streamlit UI


---

## 🏗 Tech Stack

- **Python 3.10+**
- **LangChain**
- **LangGraph**
- **OpenAI (Chat + Embeddings)**
- **FAISS / Chroma**
- **PyMuPDF (fitz)**
- **Streamlit**
- **SQLite** (for conversation history)

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/fcuriel66/AMTManApp.git
cd AMTManApp
```

### 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows

### 3. Install dependencies
pip install -r requirements.txt
