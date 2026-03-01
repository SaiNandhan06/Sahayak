# Sahayak – AI Financial Assistant 🤖💰

![Sahayak Logo](./Frontend/public/logo.jpg)

> **Sahayak** is a next-generation, intelligent conversational AI agent built to revolutionize personal finance management. Powered by advanced **Generative AI**, Sahayak processes natural language queries to help Indian users seamlessly track expenses from their bank SMS alerts, auto-categorize spending, predict recurring bills, and recommend actionable budgeting strategies alongside top fintech tools. 

---

## 🌟 Key Functional Capabilities

Sahayak bridges the gap between raw financial data and actionable insights utilizing state-of-the-art embedding models and large language models (LLMs).

- **NLP-Powered Expense Tracking**: Extract monetary values and context implicitly from SMS formats (HDFC, SBI, ICICI, UPI) without manual data entry.
- **Intelligent Spending Categorization**: Automatically classify transactions into logical buckets (Food, Travel, Utilities, Health, Entertainment).
- **Conversational Budget Guidance**: Query the assistant about the "50/30/20 Rule" or ask "Am I spending too much on food?" and get context-aware, personalized advice.
- **Fintech Recommendations**: Smart discovery of native Indian financial applications (CRED, Groww, Jar, Paytm, PhonePe) tailored exactly to the user's needs.

---

## 🛠️ Technology Stack & AI Capabilities

Sahayak incorporates a modern, modular architecture, splitting responsibilities clearly between the AI inference, reasoning backend, and interactive user interface.

### **Frontend Interface**
- **React.js & Vite**: Delivering a lightning-fast, Single-Page Application (SPA) experience.
- **Material UI (MUI)**: Customized with a striking, industrial "AI vs AI" geometric aesthetic featuring high-contrast colors (Deep Black, Vibrant Yellow, Teal) and modern typography (Montserrat).

### **Backend Engine & AI Pipeline**
- **FastAPI**: A high-performance, asynchronous Python web framework providing the API backbone.
- **LangChain**: Orchestrating complex RAG (Retrieval-Augmented Generation) chains, integrating memory, prompt templating, and model invocations.
- **Ollama (`qwen2:0.5b`)**: Local edge-AI execution using the streamlined Qwen2 language model for reliable, low-latency conversational reasoning.
- **ChromaDB**: An AI-native, open-source vector database designed perfectly for storing embeddings.
- **Nomic Embed Text (`nomic-embed-text`)**: Generating dense vector representations of financial documents to fuel the semantic search.

---

## ⚙️ How It Works (The RAG Workflow)

1. **User Input / Prompt**: The user submits a natural language question via the sleek React frontend.
2. **Context Retrieval**: The query is converted into a vector embedding. ChromaDB performs a similarity search across the pre-indexed financial knowledge base, retrieving the Top-K (3) most relevant domain-specific documents.
3. **Prompt Augmentation**: The user’s input, the conversation history (stored in-memory), and the retrieved context are stitched together into a dynamic LangChain prompt.
4. **LLM Generation**: The prompt is fed into the local Ollama LLM (`qwen2:0.5b`), which synthesizes an accurate, contextually relevant, and human-like response.
5. **Output**: The answer is streamed back via the FastAPI `/chat` endpoint and vividly displayed in the UI.

---

## 🚀 Setup Instructions

### 1. Model Preparation (Ollama)
Download and install [Ollama](https://ollama.com), then pull the required models:
```bash
ollama pull qwen2:0.5b
ollama pull nomic-embed-text
```

### 2. Backend Setup
Set up the Python environment, install dependencies, and generate the Vector DB:
```bash
# Navigate to root
cd Sahayak_Application
python -m venv venv

# Activate venv & install
venv\Scripts\activate   # Windows
# source venv/bin/activate # macOS/Linux
pip install -r requirements.txt

# Populate ChromaDB (Run once)
python data_generation.py

# Start FastAPI server
uvicorn main:app --reload
```
API Documentation available at: **http://localhost:8000/docs**

### 3. Frontend Setup
In a new terminal, run the React client:
```bash
cd Frontend
npm install --legacy-peer-deps
npm run dev
```
Client App available at: **http://localhost:5173/**

---

## 🧑‍💻 Author & Developer

**M. Sai Nandhan** — Agentic AI BootCamp 2026
Connect on LinkedIn: [M. Sainandhan](https://www.linkedin.com/in/sainandhan/)

*Empowering financial literacy through the lens of Artificial Intelligence.*
