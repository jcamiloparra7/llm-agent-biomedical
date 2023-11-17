import os

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Chroma


class DocumentProcessor:
    def __init__(
        self, literature_path: str, vector_database_path: str, embedding_model: str
    ):
        self.literature_path = literature_path
        self.vector_database_path = vector_database_path
        self.embedding_model = embedding_model

    def load_documents(self):
        pdf_loader = PyPDFDirectoryLoader(self.literature_path)
        return pdf_loader.load()

    @staticmethod
    def split_documents(docs: Document, chunk_size: int = 250, chunk_overlap: int = 30):
        text_splitter = TokenTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(docs)

    def embed_documents(self, documents: Document):
        hf_embed = HuggingFaceEmbeddings(model_name=self.embedding_model)
        return hf_embed.embed(documents)

    def persist_documents(
        self, documents: Document, collection_name: str = "medical_literature"
    ):
        db = Chroma.from_documents(
            collection_name=collection_name,
            documents=documents,
            embedding=self.embed_documents(documents),
            persist_directory=self.vector_database_path,
        )
        db.persist()


if __name__ == "__main__":
    load_dotenv()
    PDF_FOLDER_PATH = os.getenv(
        "PDF_FOLDER_PATH", "/Users/juancparra/Documents/llm-agent-biomedical/pdf_files/"
    )
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_DB_PATH = os.environ.get("VECTOR_DB_PATH")

    document_processor = DocumentProcessor(
        PDF_FOLDER_PATH, VECTOR_DB_PATH, EMBEDDING_MODEL
    )
    docs = document_processor.load_documents()
    documents = document_processor.split_documents(docs)
    document_processor.persist_documents(documents)
