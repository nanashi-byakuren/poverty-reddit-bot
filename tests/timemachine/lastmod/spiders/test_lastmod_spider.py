from timemachine import LastmodSpider


def test_parse_sitemap():
    lastmod_spider = LastmodSpider()
    lastmod: str = lastmod_spider.parse_sitemap(
        sitemap_url='https://times.abema.tv/sitemap.xml',
        target_url='https://times.abema.tv/news-article/8644234'
    )
    assert lastmod is not None, "lastmod is None"


def test_parse_sitemap_err1():
    lastmod_spider = LastmodSpider()
    lastmod: str = lastmod_spider.parse_sitemap(
        sitemap_url='https://trafficnews.jp/sitemap.xml',
        target_url='https://trafficnews.jp/post/104121'
    )
    assert lastmod is not None, "lastmod is None"


def test_local():
    pass
