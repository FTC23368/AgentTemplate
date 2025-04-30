import streamlit as st

def show_navigation():
    """
    *** THIS FUNCTION IS REDUNDANT AND CURRENTLY NOT BEING USED IN THE MAIN APP BUT USED FOR BACKEND OPERATION ***
    
    This function is only used by upload_pdf.py, which is created to upload documents for RAG. 
    This function is not used by the main chat interface for users. It is used for backend operation.
    Display a navigation menu with links to different pages of the application.
    This function creates a bordered container with navigation links using Streamlit components.
    """
    # Create a bordered container for navigation links
    with st.container(border=True):
        # Add a link to the PDF upload page with a label and icon
        st.page_link("upload_pdf.py", label="Upload PDF", icon="1️⃣")