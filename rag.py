from pathlib import Path
import json
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.schema import Document


BASE_DIR = Path(__file__).resolve().parent.parent
DOC_FILE = BASE_DIR / "data" / "ticket_attributes_text.json"
VECTORSTORE_DIR = BASE_DIR / "data" / "faiss_index"

_embeddings = None
_vectorstore = None
_qa_chain = None


def load_documents():
    with open(DOC_FILE, "r", encoding="utf-8") as f:
        content = json.load(f)["content"]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_text(content)

    return [
        Document(
            page_content=chunk,
            metadata={"source": "Freshservice Ticket Attributes"}
        )
        for chunk in chunks
    ]


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings


def build_vectorstore():
    docs = load_documents()
    vs = FAISS.from_documents(docs, get_embeddings())
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    vs.save_local(VECTORSTORE_DIR)
    return vs


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        if not VECTORSTORE_DIR.exists():
            _vectorstore = build_vectorstore()
        else:
            _vectorstore = FAISS.load_local(
                VECTORSTORE_DIR,
                get_embeddings(),
                allow_dangerous_deserialization=True
            )
    return _vectorstore


def get_llm():
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY not set")

    return ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )


def get_qa_chain():
    global _qa_chain
    if _qa_chain is None:
        _qa_chain = RetrievalQA.from_chain_type(
            llm=get_llm(),
            retriever=get_vectorstore().as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
    return _qa_chain


def answer_query(query: str):
    qa = get_qa_chain()
    result = qa(query)

    return {
        "answer": result["result"],
        "sources": list(
            {doc.metadata.get("source", "unknown")
             for doc in result["source_documents"]}
        )
    }
