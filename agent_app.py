import os
import json
import PyPDF2
import random
import streamlit as st
from src.graph import salesCompAgent
from src.google_firestore_integration import get_all_prompts
from google.oauth2 import service_account
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

# Set environment variables for Langchain and SendGrid
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="AgentTemplate"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"
os.environ['SENDGRID_API_KEY']=st.secrets['SENDGRID_API_KEY']

def initialize_prompts():

    if "credentials" not in st.session_state:
        st.session_state.credentials = get_google_cloud_credentials()
    if "prompts" not in st.session_state:
        prompts = get_all_prompts(st.session_state.credentials)
        st.session_state.prompts = prompts

def start_chat(container=st):
 
    container.title('Sales Comp Agent')
    st.markdown("#### Hey! 👋 I'm ready to assist you with all things sales comp.")
    avatars={"system":"💻🧠", "user":"🧑‍💼", "assistant":"🌀"} 
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread-id" not in st.session_state:
        st.session_state.thread_id = random.randint(1000, 9999)
    thread_id = st.session_state.thread_id

    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar=avatars[message["role"]]
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"]) 

    if prompt := st.chat_input("Ask me anything related to sales comp.."):
        escaped_prompt = prompt.replace("$", "\\$")
        st.session_state.messages.append({"role": "user", "content": escaped_prompt})
        with st.chat_message("user", avatar=avatars["user"]):
            st.write(escaped_prompt)
        
        # Initialize salesCompAgent in graph.py 
        app = salesCompAgent(st.secrets['OPENAI_API_KEY'])
        thread={"configurable":{"thread_id":thread_id}}
        
        # Stream responses from the instance of salesCompAgent which is called "app"
        for s in app.graph.stream({'initialMessage': prompt, 'sessionState': st.session_state, 
        'sessionHistory': st.session_state.messages}, thread):

            if resp := s.get("responseToUser"):
                with st.chat_message("assistant", avatar=avatars["assistant"]):
                    st.write(resp) 
                st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == '__main__':
    initialize_prompts()
    start_chat()