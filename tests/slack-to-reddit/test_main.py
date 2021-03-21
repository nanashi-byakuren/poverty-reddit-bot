import unittest
from unittest.mock import Mock

from slack_to_reddit.main import slack_to_reddit


def test_slack_to_reddit_url_verification():
    data = {'type': 'url_verification', 'challenge': 'dummy'}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert slack_to_reddit(req) == {'challenge': 'dummy'}, "challenge not matched"


def test_slack_to_reddit():
    data = {'event': {'type': 'message', 'subtype': 'bot_message',
                      'text': '<https://news.google.com/__i/rss/rd/articles/CBMiJGh0dHBzOi8vbmF0YWxpZS5tdS9jb21pYy9uZXdzLzQyMTAyMdIBKGh0dHBzOi8vYW1wLm5hdGFsaWUubXUvY29taWMvbmV3cy80MjEwMjE?oc=5|「ちびまる子ちゃん」キートン山田の卒業回で“ちょっとしたサプライズ”（コメントあり） - ナタリー>\n<https://news.google.com/__i/rss/rd/articles/CBMiJGh0dHBzOi8vbmF0YWxpZS5tdS9jb21pYy9uZXdzLzQyMTAyMdIBKGh0dHBzOi8vYW1wLm5hdGFsaWUubXUvY29taWMvbmV3cy80MjEwMjE?oc=5|「ちびまる子ちゃん」キートン山田の卒業回で“ちょっとしたサプライズ”（コメントあり）>\xa0\xa0ナタリー<https://news.google.com/__i/rss/rd/articles/CBMiRmh0dHBzOi8vYXJ0aWNsZS5hdW9uZS5qcC9kZXRhaWwvMS81LzkvMjBfOV9yXzIwMjEwMzIxXzE2MTYyODEyODE5OTExMTLSAQA?oc=5|キートン山田『ちびまる子ちゃん』ナレーション31年で卒業 さくらももこさんへの感謝と後任に助言「その人の世界で良い」>\xa0\xa0<http://auone.jp|auone.jp>&lt;a...',
                      'ts': '1616285741.000900', 'username': 'トップニュース - Google ニュース',
                      'icons': {'image_36': 'https://a.slack-edge.com/80588/img/services/rss_36.png',
                                'image_48': 'https://a.slack-edge.com/80588/img/services/rss_48.png',
                                'image_72': 'https://a.slack-edge.com/80588/img/services/rss_72.png'},
                      'bot_id': 'B0172NV7KNK', 'channel': 'C01R70X7CGG', 'event_ts': '1616285741.000900',
                      'channel_type': 'channel'}, 'type': 'event_callback', 'event_id': 'Ev01RHLY530F'
            }
    req = Mock(get_json=Mock(return_value=data), args=data)
    res = slack_to_reddit(req)
    assert 'success' in res, f"no 'success' in res: {res}"


def test_slack_to_reddit_if_error():
    data = {'event': 'broken data boo!'}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert slack_to_reddit(req) == {'message': 'error'}, "error message not matched"


if __name__ == '__main__':
    unittest.main()
