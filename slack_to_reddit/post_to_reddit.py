import os
import traceback
from os import environ
from typing import Optional, List

import praw
from praw.reddit import Submission
from prawcore import ResponseException

from logging_slack import logger, debug_to_slack

client_id = environ.get("CLIENT_ID")
client_secret = environ.get("CLIENT_SECRET")
user_agent = environ.get("USER_AGENT")
username = environ.get("USERNAME")
password = environ.get("PASSWORD")
subreddit = os.getenv("SUBREDDIT", f"u_{username}")  # subreddit指定がなければユーザーの配下

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     username=username,
                     password=password)


@logger
def exec_link_post(link_post: dict) -> Optional[Submission]:
    """
    辞書型を受け取ってSlackにPOSTする、すでに投稿済みURLの場合投稿しない
    """
    try:
        # 他の人が投稿しているか？
        dup_subs: List[Submission] = list(reddit.subreddit(subreddit).search(query=f"url:{link_post['url']}"))
        if len(dup_subs) > 0:
            debug_to_slack('重複URLなので投稿せず', link_post.__str__())
            return dup_subs[0]

        # botとして投稿する
        sub: Submission = reddit.subreddit(subreddit) \
            .submit(title=link_post['title'], url=link_post['url'])
        debug_to_slack('redditにlink post !', link_post.__str__())
        return sub
    except ResponseException as e:
        formatted_lines: List[str] = traceback.format_exc().splitlines()
        debug_to_slack(f'link postでエラー発生 {link_post}', '\n'.join(formatted_lines))
        return None
