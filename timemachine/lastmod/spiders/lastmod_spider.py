import gzip
import logging
import re
import tempfile
import traceback
from argparse import Namespace
from datetime import datetime
from os import environ
from typing import List, Optional, Tuple
from urllib.parse import urlparse, ParseResult, quote

import requests
import xmltodict as xmltodict
from dict_digger import dig
from praw import Reddit
from praw.models import Submission
from requests import Response, Session
from scrapy import Spider, Request

from timemachine.ia import ia_oldest_available_url, ia_available_url
from timemachine.util import find_item_recursive, get_permalink


class LastmodSpider(Spider):

    name = "lastmod"

    def __init__(self, *args, **kwargs):
        super(LastmodSpider, self).__init__(*args, **kwargs)
        self.submissions: List[Submission] = []
        self.args: Namespace = Namespace()
        self.self_reply = []
        self.reddit = None

    def __del__(self):
        self.reddit: Reddit = dig(self.settings.attributes, 'REDDIT').value
        dt_now: datetime = datetime.now()
        date_str: str = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')

        logging.info('===')
        logging.info('\n'.join(self.self_reply))

        # ユーザーのprofileにサブミをPOSTしたいのです
        self.reddit.subreddit(f'u_{environ.get("USERNAME")}')\
            .submit(title=f"{date_str} - タイムマシン速報判定",
                    selftext='\n'.join(self.self_reply))
        logging.info('===')

    def parse(self, response, **kwargs):
        pass

    def start_requests(self):
        assert dig(self.settings.attributes, 'SUBMISSIONS'), "submissionが１つもないです"
        self.submissions: List[Submission] = dig(self.settings.attributes, 'SUBMISSIONS').value
        self.args: Namespace = dig(self.settings.attributes, 'ARGS_OPTS').value

        for s in self.submissions:
            cb_args = {'submission': s}
            request = Request(
                s.url,
                callback=self.parse_lastmod, cb_kwargs=dict(content_dict=cb_args)
            )
            yield request

    def parse_lastmod(self, response, content_dict: dict):
        s: Submission = content_dict['submission']
        self.start_logging(s)

        # ヘッダーにある Last-Modifiedで判断（→これはあまり取得できない）
        last_modified: str = response.headers.get('Last-Modified')
        if last_modified:
            self.finish_logging(s, ('lastmod', last_modified))
            return

        if s.is_self:
            self.finish_logging(s, ('lastmod', '(リンクポストじゃ) ないです'))  # サブミッションがリンクPOSTではない
            return

        # sitemapにある更新日付を見る
        session: Session = requests.Session()
        parse_result: ParseResult = urlparse(s.url)
        # robots.txtを見に行く
        try:
            # IAに対象URLのアーカイブがあるかチェック（→ あれば最古の日付を取得する）
            archived_datetime: datetime = ia_oldest_available_url(s.url)
            if archived_datetime:
                self.finish_logging(s, ('archived_date', archived_datetime.__str__()))
                return

            res: Response = session.get(f"{parse_result.scheme}://{parse_result.netloc}/robots.txt")
            sitemap_url = f"{parse_result.scheme}://{parse_result.netloc}/sitemap.xml"

            if res.status_code != 200:
                last_modified: Optional[Tuple[str, str]] = self.parse_sitemap(sitemap_url, s.url, session)
            else:
                for line in [robots_txt for robots_txt in res.text.split("\n") if robots_txt.startswith("Sitemap:")]:
                    (_, sitemap_url) = line.split(": ")
                    last_modified: Optional[Tuple[str, str]] = self.parse_sitemap(sitemap_url, s.url, session)
                    if last_modified:
                        break

            if last_modified:
                self.finish_logging(s, last_modified)
                return

            # 何も取得できなかった…
            self.finish_logging(s, ('lastmod', '...?!'))

        except Exception as e:
            logging.error("failed to access robots.txt or sitemap.xml...")
            logging.error(traceback.format_exc())

    def parse_sitemap(
            self, sitemap_url: str, target_url: str, session: Session, depth: int = 0
    ) -> Optional[Tuple[str, str]]:
        try:
            res: Response = session.get(sitemap_url)
            if res.status_code != 200:
                logging.error(f"[depth={depth}] failed to parse {sitemap_url}, target={target_url} no sitemap")
                return None  # そもそもサイトマップがない

            # ref: https://stackoverflow.com/a/2607239/2565527
            if sitemap_url.endswith('.gz'):
                with tempfile.TemporaryFile(mode='w+b') as f:
                    f.write(res.content)
                    f.flush()
                    f.seek(0)
                    gzf = gzip.GzipFile(mode='rb', fileobj=f)
                    raw = xmltodict.parse(gzf.read())
            else:
                raw = xmltodict.parse(res.text)
            logging.debug(f"[depth={depth}] success to parse {sitemap_url}, target={target_url}")

            if dig(raw, 'sitemapindex', 'sitemap'):
                logging.debug(f"parse child sitemap size = {len(raw['sitemapindex']['sitemap'])}")
                for sitemap_dict in dig(raw, 'sitemapindex', 'sitemap'):
                    lastmod = self.parse_sitemap(sitemap_dict['loc'], target_url, session, depth+1)
                    if lastmod:
                        return lastmod

            if dig(raw, 'urlset', 'url'):
                for url_dict in raw['urlset']['url']:
                    logging.debug(url_dict)
                    if dig(url_dict, 'loc') == target_url:
                        logging.info(f"parse urls = {len(raw['urlset']['url'])}, found hooray !")
                        logging.info(f"sitemap dict => {url_dict}")

                        # 作成日時と更新日時を取得してみる
                        lastmod: Tuple[str, str] = \
                            find_item_recursive(obj=url_dict, key_r=re.compile(".*lastmod"))
                        pub_day: Tuple[str, str] = \
                            find_item_recursive(obj=url_dict, key_r=re.compile(".*publication.*"))

                        if pub_day:
                            return pub_day
                        if lastmod:
                            return lastmod
                        return 'lastmod', '(更新日付) ないです'  # sitemap.xmlに記述はあるが、最終更新日付がない等
                logging.debug(f"parse urls = {len(raw['urlset']['url'])}, not found !")

        except Exception:
            logging.error(f"sitemap_url: {sitemap_url}, target_url: {target_url}")
            logging.error(traceback.format_exc())

        return None

    def start_logging(self, s: Submission):
        logging.info(f"[START] {s.title}, url: {s.url}, \n permalink: {get_permalink(s)}")

    def finish_logging(self, s: Submission, last_modified: Tuple[str, str]):
        logging.info(f"[FINISH] {s.title}, url: {s.url}, {last_modified}")
        is_timemachine: bool = True

        if not self.args.dry_run:
            # 結果を書き込み
            pass
        if self.args.self_reply:
            # マークダウン形式
            check: str = 'x' if is_timemachine else ''
            self.self_reply.append(f"- [{s.title}]({get_permalink(s)})\n  - **{last_modified}**")



