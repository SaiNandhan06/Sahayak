"""
rag_chain.py
------------
Sahayak RAG pipeline:
  - Loads ChromaDB vector store
  - Builds a retriever (k=3)
  - Constructs a LangChain prompt with {context}, {history}, {input}
  - Exposes get_rag_response(query, history) -> str
"""

import logging
import os
from typing import List, Dict

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    RETRIEVER_K,
)

logger = logging.getLogger(__name__)

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Sahayak, a friendly and knowledgeable AI financial assistant \
designed specifically for Indian users. Your role is to:

1. Help users track and categorize expenses from SMS transaction alerts.
2. Parse and interpret Indian bank SMS formats (HDFC, SBI, ICICI, UPI apps).
3. Provide budgeting advice tailored to Indian spending habits and income levels.
4. Recommend popular Indian fintech apps (CRED, Groww, Jar, Paytm, PhonePe, ET Money).
5. Alert users when they are overspending in a category.
6. Predict recurring bills and subscriptions.

Guidelines for responding:
- Always be polite, encouraging, and non-judgmental about spending habits.
- Use Indian Rupee (₹) for all monetary values.
- Keep responses concise and actionable (3-5 sentences unless more detail is needed).
- When relevant context is provided below, use it to ground your answer.
- If you are unsure or the context does not contain the answer, say so and offer \
  a general best-practice tip.
- Do NOT make up bank account details, transaction amounts, or personal data.
- Maintain continuity with the conversation history.
"""

# ── Prompt Template ───────────────────────────────────────────────────────────
PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["context", "history", "input"],
    template=(
        f"{SYSTEM_PROMPT}\n\n"
        "=== Relevant Knowledge ===\n"
        "{context}\n\n"
        "=== Conversation History ===\n"
        "{history}\n\n"
        "=== User Message ===\n"
        "User: {input}\n\n"
        "Sahayak:"
    ),
)

# ── Lazy-loaded singletons ────────────────────────────────────────────────────
_vectorstore: Chroma | None = None
_llm: OllamaLLM | None = None


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        logger.info("Loading ChromaDB from '%s'...", CHROMA_DIR)
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        _vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_DIR,
        )
    return _vectorstore


def _get_llm() -> OllamaLLM:
    global _llm
    if _llm is None:
        logger.info("Initializing OllamaLLM with model '%s'...", LLM_MODEL)
        _llm = OllamaLLM(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    return _llm


def _format_history(history: List[Dict[str, str]]) -> str:
    """Convert session history list to a readable string."""
    if not history:
        return "No prior conversation."
    lines = []
    for turn in history:
        role = "User" if turn.get("role") == "user" else "Sahayak"
        lines.append(f"{role}: {turn.get('content', '')}")
    return "\n".join(lines)


def _format_docs(docs: List[Document]) -> str:
    """Join retrieved document page_contents with separators."""
    if not docs:
        return "No relevant context found."
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def get_rag_response(query: str, history: List[Dict[str, str]]) -> str:
    """
    Core RAG function.

    Args:
        query   : The current user message.
        history : List of {"role": "user"|"assistant", "content": "..."} dicts.

    Returns:
        The LLM-generated response string.
    """
    try:
        # 1. Retrieve top-k relevant documents
        vectorstore = _get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})
        docs = retriever.invoke(query)
        logger.info("Retrieved %d documents for query: %s", len(docs), query[:60])

        # 2. Format context and history
        context = _format_docs(docs)
        history_str = _format_history(history)

        # 3. Build the prompt
        prompt_text = PROMPT_TEMPLATE.format(
            context=context,
            history=history_str,
            input=query,
        )

        # 4. Call the LLM
        llm = _get_llm()
        response = llm.invoke(prompt_text)
        logger.info("LLM response length: %d chars", len(response))

        return response.strip()

    except Exception as e:
        logger.error("Error in get_rag_response: %s", str(e))
        raise
