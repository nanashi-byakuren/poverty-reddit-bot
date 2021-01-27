from typing import List

from dict_digger import dig
from praw.models import Submission
from scrapy import Spider, Request


class LastmodSpider(Spider):
    name = "lastmod"

    def __init__(self, *args, **kwargs):
        super(LastmodSpider, self).__init__(*args, **kwargs)
        self.submissions: List[Submission] = []

    def start_requests(self):
        assert dig(self.settings.attributes, 'SUBMISSIONS'), "submissionが１つもないです"
        self.submissions = dig(self.settings.attributes, 'SUBMISSIONS').value

        for url in [s.url for s in self.submissions]:
            self.log(f"url: {url}")
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        last_modified = response.headers.get('Last-Modified')
        self.log(f"last_modified {last_modified}")
