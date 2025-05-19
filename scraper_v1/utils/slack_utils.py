from slack_sdk import WebClient

def send_message_slack(token, message):
    # Set up a WebClient with the Slack OAuth token
    client = WebClient(token=token)

    # Send a message
    client.chat_postMessage(
        channel="indeed_de_notify", 
        text=message, 
        username="Indeed_bot"
)