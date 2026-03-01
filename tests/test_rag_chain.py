"""
tests/test_rag_chain.py
-----------------------
Unit tests for rag_chain.py.
LLM and ChromaDB retriever are mocked — no Ollama server required.
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document


# ── _format_history ───────────────────────────────────────────────────────────

def test_format_history_empty():
    from rag_chain import _format_history
    assert _format_history([]) == "No prior conversation."


def test_format_history_user_turn():
    from rag_chain import _format_history
    result = _format_history([{"role": "user", "content": "Hello"}])
    assert "User: Hello" in result


def test_format_history_multi_turn():
    from rag_chain import _format_history
    history = [
        {"role": "user", "content": "Track food"},
        {"role": "assistant", "content": "Sure!"},
    ]
    result = _format_history(history)
    assert "User: Track food" in result
    assert "Sahayak: Sure!" in result


def test_format_history_unknown_role():
    from rag_chain import _format_history
    # Unknown role should fall through to "Sahayak" label
    result = _format_history([{"role": "system", "content": "test"}])
    assert "Sahayak: test" in result


# ── _format_docs ──────────────────────────────────────────────────────────────

def test_format_docs_empty():
    from rag_chain import _format_docs
    assert _format_docs([]) == "No relevant context found."


def test_format_docs_single():
    from rag_chain import _format_docs
    docs = [Document(page_content="Food includes restaurants and groceries")]
    result = _format_docs(docs)
    assert "Food includes restaurants" in result


def test_format_docs_multiple_have_separator():
    from rag_chain import _format_docs
    docs = [Document(page_content="Doc A"), Document(page_content="Doc B")]
    result = _format_docs(docs)
    assert "Doc A" in result
    assert "Doc B" in result
    assert "---" in result


# ── PROMPT_TEMPLATE ───────────────────────────────────────────────────────────

def test_prompt_template_has_all_variables():
    from rag_chain import PROMPT_TEMPLATE
    assert "context" in PROMPT_TEMPLATE.input_variables
    assert "history" in PROMPT_TEMPLATE.input_variables
    assert "input" in PROMPT_TEMPLATE.input_variables


def test_prompt_template_renders_correctly():
    from rag_chain import PROMPT_TEMPLATE
    rendered = PROMPT_TEMPLATE.format(
        context="Some context here",
        history="User: Hi",
        input="How to save money?",
    )
    assert "Some context here" in rendered
    assert "User: Hi" in rendered
    assert "How to save money?" in rendered
    assert "Sahayak" in rendered


def test_prompt_template_contains_system_prompt():
    from rag_chain import PROMPT_TEMPLATE, SYSTEM_PROMPT
    rendered = PROMPT_TEMPLATE.format(context="x", history="y", input="z")
    # System prompt content should be injected at the top
    assert "financial assistant" in rendered.lower()


# ── get_rag_response (end-to-end mocked) ─────────────────────────────────────

@patch("rag_chain._get_llm")
@patch("rag_chain._get_vectorstore")
def test_get_rag_response_returns_string(mock_vs, mock_llm):
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = [
        Document(page_content="Food category includes restaurants")
    ]
    mock_vs.return_value.as_retriever.return_value = mock_retriever
    mock_llm.return_value.invoke.return_value = "Track via Swiggy history."

    from rag_chain import get_rag_response
    result = get_rag_response("How do I track food?", [])
    assert isinstance(result, str)
    assert len(result) > 0


@patch("rag_chain._get_llm")
@patch("rag_chain._get_vectorstore")
def test_get_rag_response_strips_whitespace(mock_vs, mock_llm):
    mock_vs.return_value.as_retriever.return_value.invoke.return_value = []
    mock_llm.return_value.invoke.return_value = "   Some answer   \n"

    from rag_chain import get_rag_response
    result = get_rag_response("test", [])
    assert result == "Some answer"


@patch("rag_chain._get_llm")
@patch("rag_chain._get_vectorstore")
def test_get_rag_response_uses_history(mock_vs, mock_llm):
    mock_vs.return_value.as_retriever.return_value.invoke.return_value = []
    captured = []
    mock_llm.return_value.invoke.side_effect = lambda p: (captured.append(p), "ok")[1]

    history = [{"role": "user", "content": "My earlier question"}]
    from rag_chain import get_rag_response
    get_rag_response("follow up", history)
    assert "My earlier question" in captured[0]


@patch("rag_chain._get_llm")
@patch("rag_chain._get_vectorstore")
def test_get_rag_response_uses_correct_k(mock_vs, mock_llm):
    mock_vs.return_value.as_retriever.return_value.invoke.return_value = []
    mock_llm.return_value.invoke.return_value = "Answer"

    from rag_chain import get_rag_response, RETRIEVER_K
    get_rag_response("test", [])
    mock_vs.return_value.as_retriever.assert_called_once_with(search_kwargs={"k": RETRIEVER_K})


@patch("rag_chain._get_llm")
@patch("rag_chain._get_vectorstore")
def test_get_rag_response_raises_on_llm_error(mock_vs, mock_llm):
    mock_vs.return_value.as_retriever.return_value.invoke.return_value = []
    mock_llm.return_value.invoke.side_effect = RuntimeError("LLM unreachable")

    from rag_chain import get_rag_response
    with pytest.raises(RuntimeError, match="LLM unreachable"):
        get_rag_response("hello", [])
