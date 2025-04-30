# This code was provided by SendGrid API

# Import required libraries
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(from_email, to_email, subject, html_content):
    # Create a Mail object with email details
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content)
    
    try:
        # Initialize SendGrid client with API key from environment variable
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        # Send the email
        response = sg.send(message)
        
        # Print response details
        print(response.status_code)
        print(response.body)
        print(response.headers)
    
    except Exception as e:
        # Print error message if sending fails
        print(e.message)