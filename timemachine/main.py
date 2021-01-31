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

reddit_instance = praw.Reddit(client_id=client_id,
                              client_secret=client_secret,
                              user_agent=user_agent,
                              username=username,
                              password=password)


def main(args: argparse.Namespace):

    # 私は誰
    print(reddit_instance.user.me())
    # NEWなスレを出す(引数でサブミのURLが指定されたらそれを使う)
    if args.submission_url:
        submissions: List[Submission] = [Submission(reddit=reddit_instance, url=args.submission_url)]
    else:
        submissions: List[Submission] = list(reddit_instance.subreddit(args.subreddit).new(limit=20))

    # settings.pyで設定された内容を取得する
    settings = get_project_settings()
    settings['SUBMISSIONS'] = submissions
    settings['ARGS_OPTS'] = args

    # スクレイピングのプロセスを動かす
    process = CrawlerProcess(settings=settings)
    process.crawl(LastmodSpider)
    process.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='リンクポストのURLをスクレイピングして更新日付をチェックし、だいぶ前ならば「タイムマシン速報」のフレアとコメントをつける'
    )
    parser.add_argument('--subreddit', required=False, default='newsokur', help='巡回対象サブレ')
    parser.add_argument('--submission-url', required=False, default=None, help='巡回したいサブミをURL指定する(デバッグ用)')
    parser.add_argument('--dry-run', required=False, action='store_true', help='「タイムマシン速報」のフレアとコメントをつけず、確認だけ行う')
    parser.add_argument('--self-reply', required=False, action='store_false', help='抽出結果をユーザー自身の場所に書き込む')
    parser.add_argument('--days-old-post', required=False, default=180, type=int, help='何日前のニュースならばタイムマシンとみなすか（デフォルト180日=半年前）')
    args: argparse.Namespace = parser.parse_args()

    # scrapyのプロジェクト名を環境変数に設定する
    environ['SCRAPY_SETTINGS_MODULE'] = 'lastmod.settings'
    main(args)
