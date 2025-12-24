import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv
from utils.document_processor import DocumentProcessor
from utils.report_generator import ReportGenerator
from utils.chat_interface import ChatInterface

# Load environment variables
load_dotenv()

# Global variables to store processed data
if 'processed_documents' not in st.session_state:
    st.session_state.processed_documents = []
if 'chat_interface' not in st.session_state:
    st.session_state.chat_interface = ChatInterface()

# Page configuration
st.set_page_config(
    page_title="Product Baseline Report (PBR) Pipeline",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Product Baseline Report (PBR) Pipeline")
    st.sidebar.title("Navigation")

    # Navigation
    page = st.sidebar.radio(
        "Choose a function:",
        ["Document Upload", "Generate Report", "Chat Interface"]
    )

    if page == "Document Upload":
        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload your documents (PDF, DOCX, XLSX, Images)",
            type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

        if uploaded_files:
            processor = DocumentProcessor()
            all_texts = []

            with st.spinner("Processing documents..."):
                for file in uploaded_files:
                    st.write(f"Processing: {file.name}")
                    try:
                        texts, tables = processor.process_file(file)
                        all_texts.extend(texts)
                        st.success(f"Successfully processed {file.name}")
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")

            if all_texts:
                st.session_state.processed_documents = all_texts
                # Build vector store
                st.session_state.chat_interface.build_vector_store(all_texts)
                st.success("All documents processed and vector store built successfully!")
            else:
                st.warning("No text content found in uploaded documents.")

    elif page == "Generate Report":
        st.header("Generate Product Baseline Report")

        if not st.session_state.processed_documents:
            st.warning("Please upload and process documents first in the 'Document Upload' section.")
        else:
            if st.button("Generate Report"):
                with st.spinner("Generating PBR..."):
                    generator = ReportGenerator(st.session_state.processed_documents)
                    report = generator.generate_report()
                    st.markdown(report)
                    st.download_button(
                        label="Download Report",
                        data=report,
                        file_name="product_baseline_report.md",
                        mime="text/markdown"
                    )

    elif page == "Chat Interface":
        st.header("Chat with Documents")

        # Check if documents are processed
        if not st.session_state.processed_documents:
            st.warning("Please upload and process documents first in the 'Document Upload' section.")
        else:
            # Get user input
            user_question = st.text_input("Ask a question about the documents:")

            if user_question:
                with st.spinner("Searching for answer..."):
                    answer = st.session_state.chat_interface.get_answer(user_question)
                    st.write("**Answer:**", answer["response"])
                    if answer["sources"]:
                        st.write("**Sources:**")
                        for source in answer["sources"]:
                            st.write(f"- {source}")

if __name__ == "__main__":
    main()
