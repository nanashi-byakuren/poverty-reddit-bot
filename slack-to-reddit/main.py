import os
from pprint import pprint

from slackeventsapi import SlackEventAdapter

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events")


@slack_events_adapter.on("message")
def slack_to_reddit(event_data):
    pprint(event_data)
    return f'Hello World!'
