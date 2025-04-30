import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage


# This function is necessary because it bridges the gap between how Streamlit stores the chat history
# and how LangChain expects the conversation context to be formatted for the language model. 
# Without this function, you'd need to do this conversion every time you want to send a message to the LLM, 
# which would lead to repetitive code.

def create_llm_message(system_prompt):
    raise Exception("ERROR.invoking deprecated function create_llm_message")
    # Initialize empty list to store messages
    resp = []
    
    # Add system prompt as the first message. This will provide the overall instructions to LLM.
    resp.append(SystemMessage(content=system_prompt))
    
    # Get chat history from Streamlit's session state
    msgs = st.session_state.messages
    
    # Iterate through chat history, and based on the role (user or assistant) tag it as HumanMessage or AIMessage
    for m in msgs:
        if m["role"] == "user":
            # Add user messages as HumanMessage
            resp.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            # Add assistant messages as AIMessage
            resp.append(AIMessage(content=m["content"]))
    
    # Return the formatted message list
    return resp


def create_llm_msg(system_prompt: str, sessionHistory: [BaseMessage]):
    #print(f"CREATELLM: sessionHistory is {sessionHistory}")
    #st.write(f"CREATELLM: sessionHistory is {sessionHistory}")
    #msgs=st.session_state.messages
    #print(f"CREATELLM  msgs is {msgs}")
    resp = []
    resp.append(SystemMessage(content=system_prompt))
    resp.extend(sessionHistory)
    #print(f"CREATELLM: resp is {resp}")
    return resp