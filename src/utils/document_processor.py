import os
import pdfplumber
from docx import Document
import pandas as pd
from PIL import Image
import pytesseract
import io

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = {
            'pdf': self._process_pdf,
            'docx': self._process_docx,
            'xlsx': self._process_excel,
            'png': self._process_image,
            'jpg': self._process_image,
            'jpeg': self._process_image
        }

    def process_file(self, file):
        """Process uploaded file based on its extension"""
        file_extension = file.name.split('.')[-1].lower()
        if file_extension in self.supported_formats:
            return self.supported_formats[file_extension](file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _process_pdf(self, file):
        """Extract text and tables from PDF"""
        texts, tables = [], []
        with pdfplumber.open(file) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                txt = page.extract_text() or ""
                texts.append({
                    "text": txt,
                    "source": file.name,
                    "page": i
                })
                # Extract tables
                for ti, table in enumerate(page.extract_tables(), start=1):
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tables.append({
                            "df": df,
                            "source": file.name,
                            "page": i,
                            "table_id": f"{i}-{ti}"
                        })
        return texts, tables

    def _process_docx(self, file):
        """Extract text from DOCX"""
        doc = Document(io.BytesIO(file.read()))
        text = "\n".join([p.text for p in doc.paragraphs])
        return [{"text": text, "source": file.name, "page": 1}], []

    def _process_excel(self, file):
        """Extract tables from Excel"""
        tables = []
        xls = pd.ExcelFile(file)
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            tables.append({
                "df": df,
                "source": file.name,
                "sheet": sheet,
                "table_id": sheet
            })
        return [], tables

    def _process_image(self, file):
        """Extract text from images using OCR"""
        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)
        return [{"text": text, "source": file.name, "page": 1}], []
