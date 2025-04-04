# -*- coding: utf-8 -*-
"""PDFextraction_20214546.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Slr_R1cAeYCxrxugur4JWOORJU4F0OST
"""

!pip install pdfplumber pymupdf pandas openpyxl

import os
import fitz  # PyMuPDF
import pandas as pd
import re
from google.colab import files

def clean_text(text):
    """
    Removes illegal characters that cannot be stored in Excel.
    """
    text = re.sub(r'[^\x20-\x7E]', '', text)  # Remove non-printable ASCII
    return text.strip()

def extract_tables_from_pdf(pdf_path, output_excel):
    """
    Extracts tables from PDFs, removes illegal characters, and saves them as an Excel file.
    """
    print(f"Processing PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    all_tables = []

    for i, page in enumerate(doc):
        text = page.get_text("text")  # Extract text
        lines = text.split("\n")
        table_data = [[clean_text(cell) for cell in line.split()] for line in lines if line.strip()]

        if len(table_data) > 1:  # Ensure there's enough data to form a table
            df = pd.DataFrame(table_data)
            df_cleaned = clean_dataframe(df)
            if not df_cleaned.empty:
                all_tables.append((i+1, df_cleaned))

    if all_tables:
        with pd.ExcelWriter(output_excel) as writer:
            for page, df in all_tables:
                df.to_excel(writer, sheet_name=f'Page_{page}', index=False, header=False)

        print(f"✅ Tables extracted and saved in {output_excel}")
    else:
        print(f"❌ No tables detected in {pdf_path}")

def clean_dataframe(df):
    """
    Cleans extracted tables by:
    - Removing empty rows/columns
    - Standardizing formatting
    - Ensuring correct row alignment
    - Removing non-printable characters
    """
    df = df.dropna(how="all", axis=0)  # Remove empty rows
    df = df.dropna(how="all", axis=1)  # Remove empty columns
    df = df.applymap(lambda x: clean_text(x) if isinstance(x, str) else x)  # Remove illegal characters
    df.fillna("", inplace=True)  # Fill missing values
    return df

def process_multiple_pdfs():
    """
    Uploads and processes multiple PDFs, saving each as a separate Excel file.
    """
    uploaded_files = files.upload()  # Upload multiple PDFs
    for pdf_file in uploaded_files.keys():
        output_excel = f"{os.path.splitext(pdf_file)[0]}.xlsx"
        extract_tables_from_pdf(pdf_file, output_excel)

    print("✅ All PDFs processed successfully!")

# Run this to upload and process multiple PDFs
process_multiple_pdfs()

from google.colab import files
files.download("extracted_tables.xlsx")