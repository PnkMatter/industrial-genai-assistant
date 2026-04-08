import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

load_dotenv()

st.set_page_config(page_title="Industrial GenAI Assistant", page_icon="🤖")
st.title("🤖 Assistente Técnico: Lições Aprendidas")

# Carregar o banco de vetores com Embeddings do Google
vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
)

# Configurar o Gemini 2.5 Flash
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
retriever = vectorstore.as_retriever()

prompt = ChatPromptTemplate.from_template(
    "Use o contexto abaixo para responder à pergunta de forma técnica e concisa. "
    "Se a resposta não estiver no contexto, diga que não encontrou informações nos manuais.\n\n"
    "Contexto:\n{context}\n\n"
    "Pergunta: {question}"
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

query = st.text_input("Descreva o problema técnico ou erro:")

if query:
    with st.spinner("Consultando base de conhecimento do Gemini..."):
        response = qa_chain.invoke(query)
        st.markdown("### Resposta Sugerida:")
        st.write(response)
        
        st.divider()
        st.caption("Nota: Esta resposta é gerada pelo Gemini 1.5 Flash baseada nos documentos locais.")