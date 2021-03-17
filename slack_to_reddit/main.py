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
google_news_ch_id: str = os.environ['GOOGLE_NEWS_CHANNEL_ID']


def slack_to_reddit(request):
    request_json: dict = request.get_json(silent=True)
    print(request_json)

    try:
        if request_json and 'type' in request_json and 'challenge' in request_json:
            return {'challenge': request_json['challenge']}

        if dig(request_json, 'event', 'channel') in subscribe_channels:
            return process_subscribe_ch(request_json)

    except:
        formatted_lines: List[str] = traceback.format_exc().splitlines()
        if dig(request_json, 'event', 'channel') in subscribe_channels:
            # botが見張っているchannelでエラーが起きたら#bot-debugチャンネルにログを吐く
            debug_to_slack('\n'.join(formatted_lines))

        print(formatted_lines)
        return {
            "message": "error"
        }


def process_subscribe_ch(request_json: dict):
    """ botが見張る対象のchannelに投稿されたメッセージを処理する """
    channel_id = dig(request_json, 'event', 'channel')

    if channel_id == google_news_ch_id:
        return process_google_news(request_json)


def process_google_news(request_json: dict):
    """ Google News用のチャンネルへの投稿を処理する """
    if request_json and 'event' in request_json and dig(request_json, 'event', 'type') == 'message':
        # Google News
        try:
            text = dig(request_json, 'event', 'text')
            print(text)
            text = text[1:-1]
            regex = re.compile(r"([^>]*)?oc=.([^>]*)>")
            short_url = regex.match(text).group(1)
            title = regex.match(text).group(2)

            opener = build_opener()
            req = Request(short_url)

            link_post = {'title': html.unescape(title), 'url': opener.open(req).geturl()}
            post_to_reddit(link_post)
        except:
            raise ValueError(dig(request_json, 'event', 'text'))


@logger
def post_to_reddit(link_post: dict):
    pass


def debug_to_slack(message: str, channel_name: str = '#bot-debug'):
    slack_client.chat_postMessage(channel=channel_name,
                                  blocks=[
                                      {
                                          "type": "section",
                                          "text": {
                                              "type": "mrkdwn",
                                              "text": "以下の部分でエラー発生",
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