"""Unit tests for RAG helpers without external services."""

import src.rag as rag


def test_get_retriever_uses_overrides(monkeypatch, tmp_path):
    captured = {}

    class FakeEmbeddings:
        def __init__(self, model_name):
            captured["model_name"] = model_name

    class FakeChroma:
        def __init__(self, persist_directory, embedding_function, collection_name):
            captured["persist_directory"] = persist_directory
            captured["collection_name"] = collection_name
            self.embedding_function = embedding_function

        def as_retriever(self, search_kwargs):
            return {"search_kwargs": search_kwargs}

    monkeypatch.setattr(rag, "HuggingFaceEmbeddings", FakeEmbeddings)
    monkeypatch.setattr(rag, "Chroma", FakeChroma)

    retriever = rag.get_retriever("birs_clean", chroma_dir=tmp_path)
    assert retriever["search_kwargs"]["k"] == rag.RAG_TOP_K
    assert captured["collection_name"] == "birs_clean"
    assert captured["persist_directory"] == str(tmp_path)
    assert captured["model_name"] == rag.EMBEDDING_MODEL


def test_get_rag_chain_builds_with_mocks(monkeypatch):
    class FakeRetriever:
        def __or__(self, other):
            return self

    monkeypatch.setattr(rag, "get_retriever", lambda name: FakeRetriever())

    class FakeLLM:
        pass

    monkeypatch.setattr(rag, "ChatOllama", lambda **kwargs: FakeLLM())

    class FakePrompt:
        def __or__(self, other):
            return self

        def __ror__(self, other):
            return self

    class FakePromptTemplate:
        @staticmethod
        def from_template(template):
            return FakePrompt()

    monkeypatch.setattr(rag, "ChatPromptTemplate", FakePromptTemplate)
    monkeypatch.setattr(rag, "StrOutputParser", lambda: object())
    monkeypatch.setattr(rag, "RunnablePassthrough", lambda: object())

    chain = rag.get_rag_chain("birs_clean")
    assert chain is not None


def test_query_rag_uses_clean_collection(monkeypatch):
    captured = {}

    class FakeChain:
        def invoke(self, question):
            captured["question"] = question
            return "answer"

    monkeypatch.setattr(rag, "get_rag_chain", lambda name: FakeChain())

    answer = rag.query_rag("Q?", use_clean_only=True)
    assert answer == "answer"
    assert captured["question"] == "Q?"


def test_query_rag_with_context(monkeypatch):
    class FakeDoc:
        def __init__(self, content):
            self.page_content = content

    class FakeRetriever:
        def invoke(self, question):
            return [FakeDoc("doc-1"), FakeDoc("doc-2")]

    monkeypatch.setattr(rag, "get_retriever", lambda name: FakeRetriever())

    class FakeLLM:
        def __or__(self, other):
            return self

        def invoke(self, payload):
            return "final-answer"

    monkeypatch.setattr(rag, "ChatOllama", lambda **kwargs: FakeLLM())

    class FakePrompt:
        def __or__(self, other):
            return self

        def invoke(self, payload):
            return "final-answer"

    class FakePromptTemplate:
        @staticmethod
        def from_template(template):
            return FakePrompt()

    monkeypatch.setattr(rag, "ChatPromptTemplate", FakePromptTemplate)
    monkeypatch.setattr(rag, "StrOutputParser", lambda: object())

    answer, contexts = rag.query_rag_with_context("Q?", use_clean_only=False)
    assert answer == "final-answer"
    assert contexts == ["doc-1", "doc-2"]
