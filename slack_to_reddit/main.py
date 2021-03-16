import os
from pprint import pprint

from attrdict import AttrDict
from slackeventsapi import SlackEventAdapter

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events")


def slack_to_reddit(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'type' in request_json:
        return {'challenge': request_json['challenge']}
    pprint(request_json)
    return f'Hello World!'
