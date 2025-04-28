import streamlit as st
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import os
import tempfile

# Get API keys from secrets
openai_api = st.secrets["OPENAI_API_KEY"]
pinecone_api = st.secrets["PINECONE_API_KEY"]
pinecone_env = st.secrets["PINECONE_ENVIRONMENT"]
index_name = st.secrets["PINECONE_INDEX_NAME"]

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = openai_api

# Initialize Pinecone
pinecone.init(api_key=pinecone_api, environment=pinecone_env)

def process_file(file, file_type):
    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_type) as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    # Load document based on file type
    if file_type == '.txt':
        loader = TextLoader(tmp_file_path)
    elif file_type == '.pdf':
        loader = PyPDFLoader(tmp_file_path)
    
    documents = loader.load()
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    
    # Create embeddings and upload to Pinecone
    embeddings = OpenAIEmbeddings()
    Pinecone.from_documents(chunks, embeddings, index_name=index_name)
    
    # Clean up temporary file
    os.unlink(tmp_file_path)
    
    return len(chunks)

# UI
st.title("Document Upload")
st.write("Upload a text or PDF file to add to the knowledge base")

uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf'])

if uploaded_file:
    file_type = os.path.splitext(uploaded_file.name)[1].lower()
    
    if st.button("Process Document"):
        with st.spinner("Processing document..."):
            try:
                num_chunks = process_file(uploaded_file, file_type)
                st.success(f"Successfully processed document into {num_chunks} chunks and uploaded to Pinecone!")
            except Exception as e:
                st.error(f"Error processing document: {str(e)}") 