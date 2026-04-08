import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv 

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

def ingest_docs():
    data_dir = os.path.join(BASE_DIR, "data")
    pdf_files = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print("⚠️ Nenhum PDF encontrado em data/.")
        return

    documents = []
    for pdf_file in pdf_files:
        path = os.path.join(data_dir, pdf_file)
        print(f"  → Carregando: {pdf_file}")
        loader = PyPDFLoader(path)
        documents.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    # 3. Criar Embeddings do Google e salvar no ChromaDB
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"),
        persist_directory=CHROMA_DIR
    )
    print("Documentos indexados com sucesso no ChromaDB usando Gemini Embeddings!")

if __name__ == "__main__":
    ingest_docs()