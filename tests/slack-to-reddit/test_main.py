import unittest
from unittest.mock import Mock

from slack_to_reddit.main import slack_to_reddit


def test_slack_to_reddit1():
    data = {'type': 'url_verification', 'challenge': 'dummy'}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert slack_to_reddit(req) == {'challenge': 'dummy'}, "challenge not matched"


def test_slack_to_reddit2():
    data = {
        'event':
            {'type': 'message', 'subtype': 'message_changed', 'hidden': True,
             'message': {'type': 'message', 'subtype': 'bot_message',
                         'text': '<https://news.google.com/__i/rss/rd/articles/CBMiOmh0dHBzOi8vd3d3Lm5ld3MyNC5qcC9zcC9hcnRpY2xlcy8yMDIxLzAzLzE2LzA3ODQwMzcyLmh0bWzSAQA?oc=5|駐車場で事故、歩行者２人心肺停止 町田市｜日テレNEWS24 - 日テレNEWS24>\n<https://news.google.com/__i/rss/rd/articles/CBMiOmh0dHBzOi8vd3d3Lm5ld3MyNC5qcC9zcC9hcnRpY2xlcy8yMDIxLzAzLzE2LzA3ODQwMzcyLmh0bWzSAQA?oc=5|駐車場で事故、歩行者２人心肺停止 町田市｜日テレNEWS24>\xa0\xa0日テレNEWS24<https://news.google.com/__i/rss/rd/articles/CBMiK2h0dHBzOi8vd3d3LnlvdXR1YmUuY29tL3dhdGNoP3Y9TkVhcU1zeVZCb0HSAQA?oc=5|駐車場で車にはねられ2人心肺停止 東京・町田(2021年3月16日)>\xa0\xa0ANNnewsCH&lt;a...',
                         'username': 'トップニュース - Google ニュース',
                         'icons': {'image_36': 'https://a.slack-edge.com/80588/img/services/rss_36.png',
                                   'image_48': 'https://a.slack-edge.com/80588/img/services/rss_48.png',
                                   'image_72': 'https://a.slack-edge.com/80588/img/services/rss_72.png'}
                         }
             }
    }
    req = Mock(get_json=Mock(return_value=data), args=data)
    res = slack_to_reddit(req)
    assert 'title' in res
    assert 'url' in res


if __name__ == '__main__':
    unittest.main()
