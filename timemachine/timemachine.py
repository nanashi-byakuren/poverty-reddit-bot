#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import environ
from os.path import dirname, join
from pathlib import Path

import praw
from dotenv import load_dotenv
from praw.models import Submission

dotenv_path = join(Path(dirname(__file__)).parent, '.env')
load_dotenv(dotenv_path)

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

# 私は誰
print(reddit.user.me())

# ホットなスレを出す
for s in reddit.subreddit('newsokur').hot(limit=20):  # type: Submission
    if not s.is_self:  # リンクポストの場合
        print(f"title: {s.title}, link: {s.url}")
