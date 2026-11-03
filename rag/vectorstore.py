import os
import shutil
from langchain_community.vectorstores import FAISS
from rag.pdf_processor import process_folder, create_text_chunks

INDEX_PATH = "faiss_index_local"


def create_vector_store(chunks: list[str], embeddings, index_path: str = INDEX_PATH):
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    vectorstore.save_local(index_path)
    return vectorstore


def load_vector_store(embeddings, index_path: str = INDEX_PATH):
    arquivo_index = os.path.join(index_path, "index.faiss")
    if os.path.exists(arquivo_index):
        return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return None


def initialize_rag_system(embeddings, context_dir: str = "data", index_dir: str = INDEX_PATH):
    needs_update = False
    index_file = os.path.join(index_dir, "index.faiss")

    if not os.path.exists(index_dir) or not os.path.exists(index_file):
        needs_update = True
    else:
        index_time = os.path.getmtime(index_file)
        if os.path.exists(context_dir):
            if os.path.getmtime(context_dir) > index_time:
                needs_update = True
            else:
                for f in os.listdir(context_dir):
                    if f.lower().endswith(".pdf"):
                        pdf_path = os.path.join(context_dir, f)
                        if os.path.getmtime(pdf_path) > index_time:
                            needs_update = True
                            break

    if not needs_update:
        vectorstore = load_vector_store(embeddings=embeddings, index_path=index_dir)
        if vectorstore:
            return vectorstore

    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)

    raw_text = process_folder(folder=context_dir)
    chunks = create_text_chunks(raw_text)
    if not chunks:
        return None

    return create_vector_store(chunks=chunks, embeddings=embeddings, index_path=index_dir)
