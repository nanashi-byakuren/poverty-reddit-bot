import os
import traceback
from typing import List

from slack_sdk import WebClient

subscribe_channels: List[str] = os.environ['SUBSCRIBE_CHANNEL_IDS'].split(",")


def logger(func):
    """ logger """
    def wrapper(*args, **kwargs):
        try:
            print(f'start {func}, args: {args}, kwargs: {kwargs}')
            result = func(*args, **kwargs)
            print(f'finish {func}, result: {result}')
            return result
        except:
            formatted_lines: List[str] = traceback.format_exc().splitlines()
            print(formatted_lines)
            return {
                "message": "error"
            }

    return wrapper


@logger
def debug_to_slack(title: str, message: str, channel_name: str = '#bot-debug'):
    slack_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    slack_client.chat_postMessage(channel=channel_name,
                                  blocks=[
                                      {
                                          "type": "section",
                                          "text": {
                                              "type": "mrkdwn",
                                              "text": title,
                                          }
                                      },
                                      {"type": "divider"},
                                      {
                                          "type": "section",
                                          "text": {
                                              "type": "mrkdwn",
                                              "text": f"```{message}```",
                                          }
                                      }
                                  ])
