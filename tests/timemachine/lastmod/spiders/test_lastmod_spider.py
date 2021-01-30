from timemachine import LastmodSpider


def test_parse_sitemap():
    lastmod_spider = LastmodSpider()
    lastmod: str = lastmod_spider.parse_sitemap(
        sitemap_url='https://this.kiji.is/sitemap.xml',
        target_url='https://this.kiji.is/728222578707513344'
    )
    assert lastmod is not None, "lastmod is None"

