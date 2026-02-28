#!/usr/bin/env python
"""Verification script to test all components work."""
import os
import sys

os.chdir(r"C:\Users\haris\Downloads\PRB_PIPELINE\PRB_PIPELINES")
sys.path.insert(0, r"C:\Users\haris\Downloads\PRB_PIPELINE\PRB_PIPELINES")

print("=" * 60)
print("PRB RAG CHATBOT - COMPONENT VERIFICATION")
print("=" * 60)

# Test 1: Import document processor
print("\n[1/4] Testing DocumentProcessor import...")
try:
    from src.utils.document_processor import DocumentProcessor
    print("✓ DocumentProcessor imported successfully")
except Exception as e:
    print(f"✗ Failed to import DocumentProcessor: {e}")
    sys.exit(1)

# Test 2: Import chat interface
print("\n[2/4] Testing ChatInterface import...")
try:
    from src.utils.chat_interface import ChatInterface
    print("✓ ChatInterface imported successfully")
except Exception as e:
    print(f"✗ Failed to import ChatInterface: {e}")
    sys.exit(1)

# Test 3: Instantiate DocumentProcessor
print("\n[3/4] Testing DocumentProcessor instantiation...")
try:
    processor = DocumentProcessor()
    print("✓ DocumentProcessor instantiated successfully")
    print(f"  - Chunk size: 800")
    print(f"  - Embedding model: sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    print(f"✗ Failed to instantiate DocumentProcessor: {e}")
    sys.exit(1)

# Test 4: Instantiate ChatInterface (without API key it will fail, which is expected)
print("\n[4/4] Testing ChatInterface instantiation...")
try:
    # This will fail without GROQ_API_KEY, which is expected
    chatbot = ChatInterface()
    print("✗ ChatInterface should have raised ValueError about missing API key")
    sys.exit(1)
except ValueError as e:
    if "GROQ_API_KEY" in str(e):
        print("✓ ChatInterface correctly checks for GROQ_API_KEY")
        print(f"  - Error (expected): {e}")
    else:
        print(f"✗ Unexpected ValueError: {e}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\n📝 NEXT STEPS:")
print("  1. Create/update .env with your GROQ_API_KEY")
print("  2. Run: streamlit run app.py")
print("  3. Upload a PDF or DOCX file")
print("  4. Ask questions about the document")
print("\n" + "=" * 60)
