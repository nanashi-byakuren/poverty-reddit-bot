import gzip
import logging
from typing import List
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

    def parse_sitemap(self, sitemap_url: str, target_url: str):
        try:
            res: Response = requests.get(sitemap_url, stream=True)

            # ref: https://stackoverflow.com/a/61171713/2565527
            if dig(res.headers._store, 'content-encoding') == ('content-encoding', 'gzip'):
                res.raw.decode_content = True
                raw = xmltodict.parse(gzip.GzipFile(fileobj=res.raw).fileobj.data)
            else:
                raw = xmltodict.parse(res.text)

            if dig(raw, 'sitemapindex', 'sitemap'):
                for sitemap_dict in dig(raw, 'sitemapindex', 'sitemap'):
                    lastmod = self.parse_sitemap(sitemap_dict['loc'], target_url)
                    if lastmod:
                        return lastmod

            for url_dict in raw['urlset']['url']:
                if url_dict["loc"] == target_url:
                    return url_dict["lastmod"]
        except Exception as e:
            logging.error(f"sitemap_url: {sitemap_url}, target_url: {target_url} {e}")
        return None

    @staticmethod
    def show_lastmod(s: Submission, last_modified: str):
        logging.info(f"{s.title}, url: {s.url}, last_modified {last_modified}")
