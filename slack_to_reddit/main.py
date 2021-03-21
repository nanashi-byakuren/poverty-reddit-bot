import html
import os
import re
import sys
import traceback
from typing import List, Optional
from urllib.request import build_opener, Request

from dict_digger import dig
from praw.reddit import Submission
from slack_sdk import WebClient

# Bot User OAuth Token, "xoxb-"から始まる文字列
from logging_slack import logger, debug_to_slack
from post_to_reddit import exec_link_post

slack_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
subscribe_channels: List[str] = os.environ['SUBSCRIBE_CHANNEL_IDS'].split(",")
google_news_ch_id: str = os.environ['GOOGLE_NEWS_CHANNEL_ID']


@logger
def slack_to_reddit(request):
    request_json: dict = request.get_json(silent=True)
    print(request_json)

    try:
        if request_json and 'type' in request_json and 'challenge' in request_json:
            return {'challenge': request_json['challenge']}

        if dig(request_json, 'event', 'channel') in subscribe_channels:
            result = process_subscribe_ch(request_json)
            if result is None:
                return {
                    "success": False,
                    "message": "error"
                }
            return result

        # 何も実行されなかった
        return {
            "success": False,
            "message": "error"
        }

    except:
        formatted_lines: List[str] = traceback.format_exc().splitlines()
        if dig(request_json, 'event', 'channel') in subscribe_channels:
            # botが見張っているchannelでエラーが起きたら#bot-debugチャンネルにログを吐く
            debug_to_slack('以下でエラー発生', '\n'.join(formatted_lines))

        print(formatted_lines)
        return {
            "message": "error"
        }


@logger
def process_subscribe_ch(request_json: dict):
    """ botが見張る対象のchannelに投稿されたメッセージを処理する """
    channel_id = dig(request_json, 'event', 'channel')

    try:
        if channel_id == google_news_ch_id:
            return process_google_news(request_json)

        return {
            "success": False,
            "message": "no subscribing channel"
        }
    except Exception as e:
        trace = sys.exc_info()[2]
        raise ValueError(e).with_traceback(trace)


@logger
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
            # 実際にRedditにlink postする
            sub: Optional[Submission] = exec_link_post({'title': html.unescape(title), 'url': opener.open(req).geturl()})
            return {
                "success": True if sub is not None else False,
                "message": f"link posted {sub if sub is not None else 'failed'}"
            }
        except Exception as e:
            trace = sys.exc_info()[2]
            raise ValueError(e).with_traceback(trace)
