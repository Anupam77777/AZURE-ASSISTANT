import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores.faiss import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
from langchain.chains import RetrievalQA
import streamlit as st

# Function to load and chunk contract text from PDF
def load_and_split_contract(file, chunk_size=1000):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    words = full_text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

# Function to embed text chunks using local sentence-transformers and create FAISS vector store
def build_vectorstore(text_chunks):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(text_chunks, embedding_model)
    return vector_store

# Create RAG QA chain using Hugging Face local model
def create_rag_qa_chain(vector_store):
    hf_pipeline = pipeline("text2text-generation", model="google/flan-t5-small")
    llm = HuggingFacePipeline(pipeline=hf_pipeline)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa_chain

# Run query on the RAG chain and get answer
def answer_query(qa_chain, question):
    return qa_chain.run(question)

# Streamlit UI
@st.cache_data
def load_data_and_create_qa(uploaded_file):
    chunks = load_and_split_contract(uploaded_file)
    vector_store = build_vectorstore(chunks)
    qa_chain = create_rag_qa_chain(vector_store)
    return qa_chain

st.title("Contract Reading RAG Bot Demo (Local Models)")

uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"])

if uploaded_file is not None:
    qa_chain = load_data_and_create_qa(uploaded_file)
    question = st.text_input("Ask a question about the contract")

    if question:
        answer = answer_query(qa_chain, question)
        st.write("Answer:", answer)
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")