from os import environ

import praw
from praw.reddit import Submission

from logging_slack import logger

client_id = environ.get("CLIENT_ID")
client_secret = environ.get("CLIENT_SECRET")
user_agent = environ.get("USER_AGENT")
username = environ.get("USERNAME")
password = environ.get("PASSWORD")

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     username=username,
                     password=password)


@logger
def exec_link_post(link_post: dict) -> Submission:
    sub: Submission = reddit.subreddit(f'u_{environ.get("USERNAME")}') \
        .submit(title=link_post['title'], url=link_post['url'])
    return sub
