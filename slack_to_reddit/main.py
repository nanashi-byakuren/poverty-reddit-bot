import html
import os
import re
import traceback
from typing import List
from urllib.request import build_opener, Request

from dict_digger import dig
from slack_sdk import WebClient

# Bot User OAuth Token, "xoxb-"から始まる文字列
from logging_slack import logger


slack_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
subscribe_channels: List[str] = os.environ['SUBSCRIBE_CHANNEL_IDS'].split(",")


def slack_to_reddit(request):
    request_json: dict = request.get_json(silent=True)
    print(request_json)

    try:
        if request_json and 'type' in request_json and 'challenge' in request_json:
            return {'challenge': request_json['challenge']}

        if request_json and 'event' in request_json and dig(request_json, 'event', 'type') == 'message':
            # Google News
            text = dig(request_json, 'event', 'message', 'text')
            text = text[1:-1]
            regex = re.compile(r"([^>]*)?oc=.([^>]*)>")
            short_url = regex.match(text).group(1)
            title = regex.match(text).group(2)

            opener = build_opener()
            req = Request(short_url)

            return {'title': html.unescape(title), 'url': opener.open(req).geturl()}
    except:
        formatted_lines: List[str] = traceback.format_exc().splitlines()
        if dig(request_json, 'event', 'channel') in subscribe_channels:
            # botが見張っているchannelでエラーが起きたら#bot-debugチャンネルにログを吐く
            debug_to_slack('\n'.join(formatted_lines))

        print(formatted_lines)
        return {
            "message": "error"
        }


def debug_to_slack(message: str, channel_name: str = '#bot-debug'):
    slack_client.chat_postMessage(channel=channel_name,
                                  blocks=[
                                      {
                                          "type": "section",
                                          "text": {
                                              "type": "mrkdwn",
                                              "text": message,
                                          }
                                      }
                                  ])