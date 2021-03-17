import os
import traceback
from typing import List

from slack_sdk import WebClient

subscribe_channels: List[str] = os.environ['SUBSCRIBE_CHANNEL_IDS'].split(",")


def logger(func):
    """ logger """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            formatted_lines: List[str] = traceback.format_exc().splitlines()
            slack_client: WebClient = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
            slack_client.chat_postMessage(channel='#bot-debug',
                                          blocks=[
                                              {
                                                  "type": "section",
                                                  "text": {
                                                      "type": "mrkdwn",
                                                      "text": '\n'.join(formatted_lines),
                                                  }
                                              }
                                          ])
            return {
                "message": "error"
            }

    return wrapper
