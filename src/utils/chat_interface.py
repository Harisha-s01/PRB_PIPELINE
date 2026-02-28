import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ChatInterface:
    def __init__(self):
        load_dotenv()

        groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")

        # Groq LLM
        # Using llama-3.3-70b-versatile (latest supported model)
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )

        # The vector store / retriever aren't known until the document
        # has been processed in the Streamlit app.  We lazily create the RAG
        # chain later via `create_vector_store`.
        self.qa_chain = None

    def create_vector_store(self, vector_store):
        """Initialize the retrieval chain using a FAISS vector store.

        Builds a simple RAG chain: retrieve relevant documents, then pass
        them to the LLM along with the user's question.
        """

        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        # Define the prompt template for the QA chain
        template = """You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Build the chain using LCEL (LangChain Expression Language)
        # Format retrieved documents into a context string
        def format_docs(docs):
            return "\n\n".join([doc.page_content for doc in docs])
        
        # Create the chain: retriever -> format docs -> prompt -> llm -> output parser
        self.qa_chain = (
            {
                "context": retriever | RunnablePassthrough(func=format_docs),
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query):
        if self.qa_chain is None:
            raise RuntimeError("ChatInterface has no vector store; call create_vector_store first")
        response = self.qa_chain.invoke(query)
        return response