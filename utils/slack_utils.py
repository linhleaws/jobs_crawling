import os
from slack_sdk import WebClient

def send_message_slack(message):
    token = os.getenv('SLACK_TOKEN')
    # Set up a WebClient with the Slack OAuth token
    client = WebClient(token=token)

    # Send a message
    client.chat_postMessage(
        channel="indeed_de_notify", 
        text=message, 
        username="Indeed_bot"
)