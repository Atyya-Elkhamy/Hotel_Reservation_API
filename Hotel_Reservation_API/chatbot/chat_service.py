from langchain.chains import RetrievalQA
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import DirectoryLoader
from langchain.prompts import PromptTemplate
import os
from django.conf import settings
import logging
from typing import Optional, Literal

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
                # doc_path = os.path.join(settings.BASE_DIR, "Hotel Reservation Website Documentation.markdown")
                # Load and process documents
                # loader = UnstructuredFileLoader(doc_path)

                docs_dir = os.path.join(settings.BASE_DIR, "docs")
                loader = DirectoryLoader(docs_dir, glob="**/*.*")

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

                # Initialize both LLMs
                # Gemini - primary model
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    temperature=0.2,
                    google_api_key=  os.environ.get("GOOGL_API_KEY")
                )

                # Ollama - fallback model
                self.ollama_llm = Ollama(model="llama3")

                # Initialize QA chains for both models
                self.gemini_chain = RetrievalQA.from_chain_type(
                    self.gemini_llm,
                    retriever=self.db.as_retriever(),
                    chain_type_kwargs={
                        "prompt": PromptTemplate(
                            template="Answer the question based on the context below. Provide a direct, helpful response without mentioning the source documents or referring to 'this document'. \n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
                            input_variables=["context", "question"]
                        )
                    }
                    # return_source_documents=True
                )

                self.ollama_chain = RetrievalQA.from_chain_type(
                    self.ollama_llm,
                    retriever=self.db.as_retriever()
                )

                self._initialized = True
                logger.info("QA Service initialized successfully with Gemini and Ollama")

            except Exception as e:
                logger.error(f"Error initializing QA Service: {str(e)}")
                raise

    def get_answer(self, question: str, model: Optional[Literal["gemini", "ollama"]] = "gemini"):
        """
        Get an answer to a question using the specified model.

        Args:
            question: The question to answer
            model: Which model to use - "gemini" (default) or "ollama"

        Returns:
            The answer to the question
        """
        try:
            # Use the specified model, or fall back to the other model if there's an error
            if model == "gemini":
                try:
                    result = self.gemini_chain.invoke({"query": question})

                    # Add source info from retrieved documents if available
                    source_info = ""
                    # if 'source_documents' in result and result['source_documents']:
                    #     source_info = "\n\nSources:\n"
                    #     for i, doc in enumerate(result['source_documents'][:3]):  # Limit to top 3 sources
                    #         if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                    #             source_info += f"- {doc.metadata['source']}\n"

                    return result['result'].strip() #+ source_info

                except Exception as e:
                    logger.warning(f"Gemini error, falling back to Ollama: {str(e)}")
                    model = "ollama"

            if model == "ollama":
                result = self.ollama_chain.invoke({"query": question})
                return result['result'].strip()

        except Exception as e:
            error_msg = f"Error processing question: {str(e)}"
            logger.error(error_msg)
            return f"Sorry, an error occurred while processing your question: {str(e)}"

    def get_answer_with_model_choice(self, question: str, model: Optional[Literal["gemini", "ollama"]] = "gemini"):
        """
        Get an answer to a question and specify which model answered it.

        Args:
            question: The question to answer
            model: Which model to use - "gemini" (default) or "ollama"

        Returns:
            A dictionary containing the answer and which model was used
        """
        try:
            original_model_choice = model

            # Try with requested model first
            if model == "gemini":
                try:
                    result = self.gemini_chain.invoke({"query": question})
                    used_model = "gemini"
                except Exception as e:
                    logger.warning(f"Gemini error, falling back to Ollama: {str(e)}")
                    result = self.ollama_chain.invoke({"query": question})
                    used_model = "ollama"
            else:  # model == "ollama"
                try:
                    result = self.ollama_chain.invoke({"query": question})
                    used_model = "ollama"
                except Exception as e:
                    logger.warning(f"Ollama error, falling back to Gemini: {str(e)}")
                    result = self.gemini_chain.invoke({"query": question})
                    used_model = "gemini"

            # Format the answer and add model info
            answer = result['result'].strip()

            # Add source info if using Gemini and sources are available
            # if used_model == "gemini" and 'source_documents' in result and result['source_documents']:
            #     source_info = "\n\nSources:\n"
            #     for i, doc in enumerate(result['source_documents'][:3]):  # Limit to top 3 sources
            #         if hasattr(doc, 'metadata') and 'source' in doc.metadata:
            #             source_info += f"- {doc.metadata['source']}\n"
            #     answer += source_info

            return {
                "answer": answer,
                "model_used": used_model,
                "model_requested": original_model_choice,
                "fallback_used": used_model != original_model_choice
            }

        except Exception as e:
            error_msg = f"Error processing question with both models: {str(e)}"
            logger.error(error_msg)
            return {
                "answer": f"Sorry, an error occurred while processing your question: {str(e)}",
                "model_used": "none",
                "model_requested": original_model_choice,
                "fallback_used": True,
                "error": str(e)
            }