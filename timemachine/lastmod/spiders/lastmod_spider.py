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
        self.submissions: List[Submission] = dig(self.settings.attributes, 'SUBMISSIONS').value

        for s in self.submissions:
            cb_args = {'submission': s}
            request = Request(
                s.url,
                callback=self.parse_lastmod, cb_kwargs=dict(content_dict=cb_args)
            )
            yield request

    def parse_lastmod(self, response, content_dict: dict):
        last_modified = response.headers.get('Last-Modified')
        submission: Submission = content_dict['submission']
        self.log(f"{submission.title}, last_modified {last_modified}")
