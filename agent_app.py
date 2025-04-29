import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import pinecone
import os

# Set API keys from secrets
openai_api = st.secrets["OPENAI_API_KEY"]
pinecone_api = st.secrets["PINECONE_API_KEY"]
pinecone_env = st.secrets["PINECONE_ENVIRONMENT"]
index_name = st.secrets["PINECONE_INDEX_NAME"]
langsmith_api_key = st.secrets["LANGSMITH_API_KEY"]
agent_template = st.secrets.get("LANGSMITH_PROJECT", "default")

# Set API keys and environment variables
os.environ["OPENAI_API_KEY"] = openai_api
os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
os.environ["LANGCHAIN_PROJECT"] = agent_template
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Initialize Pinecone
pinecone.init(api_key=pinecone_api, environment=pinecone_env)
index = pinecone.Index(index_name)

# Embedding + Vector Store
embed_model = OpenAIEmbeddings()
vectorstore = Pinecone.from_existing_index(index_name=index_name, embedding=embed_model, text_key="text")

# Retrieval-based QA chain
llm = ChatOpenAI(temperature=0)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# UI design
st.title("My AI Agent")
query = st.text_input("Ask me something:")
if query:
    response = qa_chain.run(query)
    st.write(response)