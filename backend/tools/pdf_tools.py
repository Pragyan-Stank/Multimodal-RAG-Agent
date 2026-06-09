import re
from pathlib import Path
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.config import PROJECT_ROOT, embeddings

@tool
def pdf_parser(file_path: str) -> dict:
    """
    Parse PDF and extract full text + URLs.
    """

    try:
        path = Path(file_path)

        if not path.is_absolute():
            path = PROJECT_ROOT / path

        path = path.resolve()

        if not path.exists():
            return {
                "success": False,
                "error": f"PDF not found: {path}"
            }

        loader = PyPDFLoader(str(path))
        docs = loader.load()

        full_text = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        urls = list(
            set(
                re.findall(
                    r"https?://[^\s<>\"]+",
                    full_text
                )
            )
        )

        return {
            "success": True,
            "file_path": str(path),
            "num_pages": len(docs),
            "content": full_text,
            "urls": urls
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }




@tool
def document_retriever(
    document_content: str,
    query: str,
    k: int = 5
) -> dict:
    """
    Retrieve relevant chunks from extracted document text.
    """

    try:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.create_documents(
            [document_content]
        )

        vector_store = FAISS.from_documents(
            chunks,
            embeddings
        )

        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

        docs = retriever.invoke(query)

        return {
            "success": True,
            "retrieved_context": [
                doc.page_content
                for doc in docs
            ]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
