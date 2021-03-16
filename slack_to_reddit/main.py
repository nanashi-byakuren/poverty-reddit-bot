import html
import os
import re
from urllib.request import build_opener, Request

from dict_digger import dig
from slack_sdk import WebClient

# Bot User OAuth Token, "xoxb-"から始まる文字列
from slack_to_reddit.logging_slack import logger


slack_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])


@logger
def slack_to_reddit(request):
    request_json = request.get_json(silent=True)
    print(request_json)

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

    raise ValueError
