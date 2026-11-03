import os
try:
    from PyPDF2 import PdfReader
except ImportError:
    from pypdf import PdfReader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


def process_pdf(file_path: str) -> str:
    text = ""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def process_folder(folder: str = "data") -> str:
    all_text = ""
    if not os.path.exists(folder):
        return ""

    for file in sorted(os.listdir(folder)):
        if file.lower().endswith(".pdf"):
            path = os.path.join(folder, file)
            all_text += process_pdf(path) + "\n"
    return all_text


def create_text_chunks(text: str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return text_splitter.split_text(text)
