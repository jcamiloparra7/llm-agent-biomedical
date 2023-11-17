import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

load_dotenv()


class MedicalAssistant:
    ONLINE_LIBRARY_PATH = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf"
    VECTOR_DB_PATH = os.environ.get("VECTOR_DB_PATH")
    COLLECTION_NAME = os.environ.get("COLLECTION_NAME")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

    def __init__(self) -> None:
        self.retrieval_chain = self._get_retrieval_chain(
            self.EMBEDDING_MODEL,
            self.COLLECTION_NAME,
            self.VECTOR_DB_PATH,
            self.OPENAI_MODEL,
        )

    def _get_retrieval_chain(
        self, embedding_model, collection_name, vector_db_path, openai_model
    ):
        hf_embed = HuggingFaceEmbeddings(model_name=embedding_model)
        db = Chroma(
            collection_name=collection_name,
            embedding_function=hf_embed,
            persist_directory=vector_db_path,
        )
        llm = ChatOpenAI(model=openai_model, temperature=0)
        retrieval_chain = RetrievalQA.from_chain_type(
            llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={"k": 10}),
            return_source_documents=True,
        )
        return retrieval_chain

    def answer_query(self, query: str) -> str:
        try:
            raw_response = self.retrieval_chain.invoke(
                f'{query} - be extensive in your response'
            )
            formatted_answer = self._prettify_response(raw_response)
            return formatted_answer
        except Exception as error:
            return error

    def _prettify_response(self, raw_response: dict):
        references_list = set(self._format_documents(raw_response["source_documents"]))
        formated_references = self._format_as_markdown_references(references_list)
        return f'{raw_response["result"]}  \n  \n{formated_references}'

    def _format_documents(self, documents):
        formatted_docs = []
        for doc in documents:
            # Extract the source path from the metadata
            full_path = doc.metadata["source"]
            # Split the path by 'biomedical_pdf_files' and take the second part
            postfix = full_path.split("biomedical_pdf_files")[-1]
            # Add the postfix to the list
            formatted_docs.append(postfix)
        return formatted_docs

    def _format_as_markdown_references(self, paths):
        references = []
        for path in paths:
            reference = f"{self.ONLINE_LIBRARY_PATH}{path}  "
            # Two spaces at the end for a markdown line break
            references.append(reference)
        return "\n".join(references)
