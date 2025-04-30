# src/feedback_collector_agent.py

from typing import List
from src.create_llm_message import create_llm_message, create_llm_msg
from src.send_email import send_email
from src.prompt_store import get_prompt
from langchain_core.messages import BaseMessage

# When FeedbackCollectorAgent object is created, it's initialized with a client, a model, and an index. 
# The main entry point is the feedback_collector_agent method. You can see workflow.add_node for feedback_collector_agent 
# node in graph.py

class FeedbackCollectorAgent:
    
    def __init__(self, model):
        """
        Initialize the FeedbackCollectorAgent with necessary components.
        
        :param model: Language model for generating responses
        """
        self.model = model


    def generate_response(self, user_query: str, messageHistory: [BaseMessage]) -> str:
        """
        Generate a response based on user query.
        
        :param user_query: Original user query
        :return: Generated response string
        """
        # Get feedback collector prompt from prompt_store.py 
        feedback_collector_prompt = get_prompt("feedbackcollector")

        # Create a well-formatted message for LLM by passing the retrieved information above to create_llm_msg
        llm_messages = create_llm_msg(feedback_collector_prompt, messageHistory)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        llm_response = self.model.invoke(llm_messages)

        # Extract the content attribute from the llm_response object 
        feedback_collector_response = llm_response.content

        return feedback_collector_response

    def feedback_collector_agent(self, state: dict) -> dict:
        """
        Main entry point for feedback related queries.
        
        :param state: Current state dictionary containing user's initial message
        :return: Updated state dictionary with generated response and category
        """
        
        # Generate a response using the retrieved documents and the user's initial message
        full_response = self.generate_response(state['initialMessage'], state['message_history'])
        send_email('malihajburney@gmail.com', 'i_jahangir@hotmail.com', "Feedback for Sales Comp", full_response)
        
        # Return the updated state with the generated response and the category set to 'policy'
        return {
            "lnode": "feedback_collector_agent", 
            "responseToUser": full_response,
            "category": "feedbackcollector"
        }