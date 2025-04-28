from langchain.chains import RetrievalQA
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class QAService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QAService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            try:
                # Path to the documentation file
                doc_path = os.path.join(settings.BASE_DIR, "Hotel Reservation Website Documentation.markdown")

                # Load and process documents
                loader = UnstructuredFileLoader(doc_path)
                docs = loader.load()

                text_splitter = CharacterTextSplitter(
                    separator="\n",
                    chunk_size=2000,
                    chunk_overlap=200
                )
                texts = text_splitter.split_documents(docs)

                # Create embeddings and vector store
                embeddings = HuggingFaceEmbeddings()
                self.db = FAISS.from_documents(texts, embeddings)

                # Initialize LLM and QA chain
                llm = Ollama(model="llama3")
                self.chain = RetrievalQA.from_chain_type(
                    llm,
                    retriever=self.db.as_retriever()
                )

                self._initialized = True
                logger.info("QA Service initialized successfully")

            except Exception as e:
                logger.error(f"Error initializing QA Service: {str(e)}")
                raise

    def get_answer(self, question):
        try:
            result = self.chain.invoke({"query": question})
            return result['result'].strip()
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return f"Sorry, an error occurred while processing your question: {str(e)}"