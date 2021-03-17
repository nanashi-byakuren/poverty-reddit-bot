import os
from typing import List

from slack_sdk import WebClient

subscribe_channels: List[str] = os.environ['SUBSCRIBE_CHANNEL_IDS'].split(",")


def logger(func):
    """ logger """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            slack_client: WebClient = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
            slack_client.chat_postMessage(channel='#bot-debug',
                                          blocks=[
                                              {
                                                  "type": "section",
                                                  "text": {
                                                      "type": "mrkdwn",
                                                      "text": "以下をRedditにPOST",
                                                  }
                                              },
                                              {"type": "divider"},
                                              {
                                                  "type": "section",
                                                  "text": {
                                                      "type": "mrkdwn",
                                                      "text": '\n'.join(args),
                                                  }
                                              }
                                          ])
            return {
                "message": "error"
            }

    return wrapper
