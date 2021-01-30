import logging
from typing import List
from urllib.parse import urlparse, ParseResult

import requests
import xmltodict as xmltodict
from dict_digger import dig
from praw.models import Submission
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

    @staticmethod
    def parse_sitemap(sitemap_url: str, target_url: str) -> str:
        res = requests.get(sitemap_url)
        raw = xmltodict.parse(res.text)

        for url_dict in raw['urlset']['url']:
            if url_dict["loc"] == target_url:
                return url_dict["lastmod"]

    @staticmethod
    def show_lastmod(s: Submission, last_modified: str):
        logging.info(f"{s.title}, url: {s.url}, last_modified {last_modified}")
