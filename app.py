import streamlit as st
from src.utils.document_processor import DocumentProcessor
from src.utils.chat_interface import ChatInterface

st.set_page_config(page_title="PBR RAG Chatbot")

st.title("PBR Document RAG Chatbot")

if "chatbot" not in st.session_state:
    # create an empty chatbot; the vector store will be attached after
    # the user uploads and processes a document.
    st.session_state.chatbot = ChatInterface()

if "chunks_created" not in st.session_state:
    st.session_state.chunks_created = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

processor = DocumentProcessor()

uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])

if uploaded_file and not st.session_state.chunks_created:
    with st.spinner("Processing document..."):
        text = processor.extract_text(uploaded_file)
        chunks = processor.chunk_text(text)
        # build the FAISS store from the chunks, then hand it to the
        # chatbot that lives in session state
        vector_store = processor.create_vector_store(chunks)
        st.session_state.chatbot.create_vector_store(vector_store)
        st.session_state.chunks_created = True

    st.success("Document processed successfully.")

query = st.text_input("Ask a question about the document:")

if query and st.session_state.chunks_created:
    with st.spinner("Generating answer..."):
        # the ChatInterface exposes `ask`, not `generate_answer`
        answer = st.session_state.chatbot.ask(query)

    st.session_state.chat_history.append(("You", query))
    st.session_state.chat_history.append(("AI", answer))

for role, message in st.session_state.chat_history:
    st.markdown(f"**{role}:** {message}")