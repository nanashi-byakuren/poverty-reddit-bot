#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from os import environ
from os.path import dirname, join
from pathlib import Path
from typing import List

import praw
from dotenv import load_dotenv
from praw.models import Submission
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from timemachine.lastmod.spiders.lastmod_spider import LastmodSpider

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


def main(args):

    # 私は誰
    print(reddit.user.me())
    # ホットなスレを出す
    submissions: List[Submission] = list(reddit.subreddit(args.subreddit).new(limit=20))

    # settings.pyで設定された内容を取得する
    settings = get_project_settings()
    settings['SUBMISSIONS'] = submissions

    # スクレイピングのプロセスを動かす
    process = CrawlerProcess(settings=settings)
    process.crawl(LastmodSpider)
    process.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='リンクポストのURLをスクレイピングして更新日付をチェックし、だいぶ前ならば「タイムマシン速報」のフレアとコメントをつける'
    )
    parser.add_argument('--subreddit', required=False, default='newsokur', help='巡回対象サブレ')
    args = parser.parse_args()

    # scrapyのプロジェクト名を環境変数に設定する
    environ['SCRAPY_SETTINGS_MODULE'] = 'lastmod.settings'
    main(args)
