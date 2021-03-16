import os
import traceback

from slack_sdk import WebClient


def logger(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            formatted_lines = traceback.format_exc().splitlines()
            slack_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
            slack_client.chat_postMessage(channel='#bot-debug', blocks=formatted_lines)
            return {
                "message": "error"
            }

    return wrapper
