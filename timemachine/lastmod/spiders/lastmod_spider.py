import gzip
import logging
import re
import tempfile
import traceback
from typing import List, Optional, Pattern, Tuple
from urllib.parse import urlparse, ParseResult, quote

import requests
import xmltodict as xmltodict
from dict_digger import dig
from praw.models import Submission
from requests import Response, Session
from scrapy import Spider, Request


class LastmodSpider(Spider):

    name = "lastmod"

    def __init__(self, *args, **kwargs):
        super(LastmodSpider, self).__init__(*args, **kwargs)
        self.submissions: List[Submission] = []

    def parse(self, response, **kwargs):
        pass

    def start_requests(self):
        assert dig(self.settings.attributes, 'SUBMISSIONS'), "submissionが１つもないです"
        self.submissions: List[Submission] = dig(self.settings.attributes, 'SUBMISSIONS').value

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
            self.finish_logging(s, last_modified)

        # sitemapにある更新日付を見る
        session: Session = requests.Session()
        parse_result: ParseResult = urlparse(s.url)
        # robots.txtを見に行く
        try:
            res: Response = session.get(f"{parse_result.scheme}://{parse_result.netloc}/robots.txt")
            for line in [robots_txt for robots_txt in res.text.split("\n") if robots_txt.startswith("Sitemap:")]:
                (_, sitemap_url) = line.split(": ")
                if not sitemap_url:  # もしrobots.txtに何もなければ決め打ちで取得する
                    sitemap_url = f"{parse_result.scheme}://{parse_result.netloc}/sitemap.xml"
                last_modified: Optional[Tuple[str, str]] = self.parse_sitemap(sitemap_url, s.url, session)
                if last_modified:
                    self.finish_logging(s, last_modified)
                    return
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
                            find_item_recursive(obj=url_dict, key_r=re.compile(".*publication_date"))

                        if pub_day:
                            return pub_day
                        if lastmod:
                            return lastmod
                        return 'lastmod', '(更新日付) ないです'  # sitemap.xmlに記述はあるが、最終更新日付がない等
                logging.debug(f"parse urls = {len(raw['urlset']['url'])}, not found !")

        except Exception as e:
            logging.error(f"sitemap_url: {sitemap_url}, target_url: {target_url}")
            logging.error(traceback.format_exc())

        return None

    @staticmethod
    def start_logging(s: Submission):
        logging.info(f"[START] {s.title}, url: {s.url}, \n permalink: https://www.reddit.com{quote(s.permalink)}")

    @staticmethod
    def finish_logging(s: Submission, last_modified: Tuple[str, str]):
        logging.info(f"[FINISH] {s.title}, url: {s.url}, {last_modified}")


def find_item_recursive(obj: dict, key_r: Pattern) -> Optional[Tuple[str, str]]:
    matched_keys = list(filter(key_r.match, obj.keys()))
    if len(matched_keys) > 0:
        key: str = matched_keys[0]
        return key, obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = find_item_recursive(obj=v, key_r=key_r)
            if item is not None:
                return item
    return None
