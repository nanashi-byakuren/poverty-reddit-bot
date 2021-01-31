import gzip
import logging
import tempfile
import traceback
from typing import List, Optional
from urllib.parse import urlparse, ParseResult

import requests
import xmltodict as xmltodict
from dict_digger import dig
from praw.models import Submission
from requests import Response
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
        # ヘッダーにある Last-Modifiedで判断（→これはあまり取得できない）
        last_modified: str = response.headers.get('Last-Modified')
        s: Submission = content_dict['submission']
        if last_modified:
            self.show_lastmod(s, last_modified)
        # sitemapにある更新日付を見る
        parse_result: ParseResult = urlparse(s.url)
        sitemap_url = f"{parse_result.scheme}://{parse_result.netloc}/sitemap.xml"
        last_modified = self.parse_sitemap(sitemap_url, s.url)
        if last_modified:
            self.show_lastmod(s, last_modified)

    def parse_sitemap(self, sitemap_url: str, target_url: str, depth: int = 0) -> Optional[str]:
        try:
            res: Response = requests.get(sitemap_url)
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
                    lastmod = self.parse_sitemap(sitemap_dict['loc'], target_url, depth+1)
                    if lastmod:
                        return lastmod

            if dig(raw, 'urlset', 'url'):
                for url_dict in raw['urlset']['url']:
                    logging.debug(url_dict)
                    if dig(url_dict, 'loc') == target_url:
                        logging.info(f"parse urls = {len(raw['urlset']['url'])}, found hooray !")
                        logging.info(f"sitemap dict => {url_dict}")
                        if dig(url_dict, 'lastmod'):
                            return dig(url_dict, 'lastmod')
                        return '(更新日付) ないです'  # sitemap.xmlに記述はあるが、最終更新日付がない
                logging.debug(f"parse urls = {len(raw['urlset']['url'])}, not found !")

        except Exception as e:
            logging.error(f"sitemap_url: {sitemap_url}, target_url: {target_url}")
            logging.error(traceback.format_exc())

        return None

    @staticmethod
    def show_lastmod(s: Submission, last_modified: str):
        logging.info(f"{s.title}, url: {s.url}, last_modified {last_modified}")
