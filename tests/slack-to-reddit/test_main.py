import unittest
from unittest.mock import Mock

from slack_to_reddit.main import slack_to_reddit


def test_slack_to_reddit_url_verification():
    data = {'type': 'url_verification', 'challenge': 'dummy'}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert slack_to_reddit(req) == {'challenge': 'dummy'}, "challenge not matched"


def test_slack_to_reddit():
    data = {'event': {'type': 'message', 'subtype': 'message_changed', 'hidden': True,
                      'message': {'type': 'message', 'subtype': 'bot_message',
                                  'text': '<https://news.google.com/__i/rss/rd/articles/CBMiMGh0dHBzOi8vbmV3cy5teW5hdmkuanAvYXJ0aWNsZS8yMDIxMDMyNy0xODQ2NzI5L9IBAA?oc=5|関ジャニ∞、『サタデープラス』テーマソング歌う! 丸山隆平「想いを込めて」 - マイナビニュース>\n<https://news.google.com/__i/rss/rd/articles/CBMiMGh0dHBzOi8vbmV3cy5teW5hdmkuanAvYXJ0aWNsZS8yMDIxMDMyNy0xODQ2NzI5L9IBAA?oc=5|関ジャニ∞、『サタデープラス』テーマソング歌う! 丸山隆平「想いを込めて」>\xa0\xa0マイナビニュース<https://news.google.com/__i/rss/rd/articles/CBMiJGh0dHBzOi8vbWRwci5qcC9tdXNpYy9kZXRhaWwvMjUwMjY0OdIBIWh0dHBzOi8vbWRwci5qcC9tdXNpYy9hbXAvMjUwMjY0OQ?oc=5|関ジャニ∞「サタデープラス」テーマソングを担当>\xa0\xa0モデルプレス&lt;a...',
                                  'username': 'トップニュース - Google ニュース',
                                  'icons': {'image_36': 'https://a.slack-edge.com/80588/img/services/rss_36.png',
                                            'image_48': 'https://a.slack-edge.com/80588/img/services/rss_48.png',
                                            'image_72': 'https://a.slack-edge.com/80588/img/services/rss_72.png'},
                                  'bot_id': 'B0172NV7KNK', 'attachments': [
                              {'service_name': 'マイナビニュース', 'title': '関ジャニ∞、『サタデープラス』テーマソング歌う! 丸山隆平「想いを込めて」',
                               'title_link': 'https://news.google.com/__i/rss/rd/articles/CBMiMGh0dHBzOi8vbmV3cy5teW5hdmkuanAvYXJ0aWNsZS8yMDIxMDMyNy0xODQ2NzI5L9IBAA?oc=5',
                               'text': '4月から放送時間を30分拡大し、7時30分からスタートするMBS・TBS系情報番組『サタデープラス』。それを記念して、関ジャニ∞がオリジナル番組テーマソングを歌うことが決定した。テーマソング「サタデーソング」はリニューアル初回の4月3日の放送でお披露目される。',
                               'fallback': 'マイナビニュース: 関ジャニ∞、『サタデープラス』テーマソング歌う! 丸山隆平「想いを込めて」',
                               'image_url': 'https://news.mynavi.jp/article/20210327-1846729/index_images/index.jpg',
                               'ts': 1616804700,
                               'from_url': 'https://news.google.com/__i/rss/rd/articles/CBMiMGh0dHBzOi8vbmV3cy5teW5hdmkuanAvYXJ0aWNsZS8yMDIxMDMyNy0xODQ2NzI5L9IBAA?oc=5',
                               'image_width': 375, 'image_height': 250, 'image_bytes': 249251,
                               'service_icon': 'https://news.mynavi.jp/favicon.ico', 'id': 1,
                               'original_url': 'https://news.google.com/__i/rss/rd/articles/CBMiMGh0dHBzOi8vbmV3cy5teW5hdmkuanAvYXJ0aWNsZS8yMDIxMDMyNy0xODQ2NzI5L9IBAA?oc=5'},
                              {'service_name': 'モデルプレス - ライフスタイル・ファッションエンタメニュース',
                               'title': '関ジャニ∞「サタデープラス」テーマソングを担当 - モデルプレス',
                               'title_link': 'https://news.google.com/__i/rss/rd/articles/CBMiJGh0dHBzOi8vbWRwci5qcC9tdXNpYy9kZXRhaWwvMjUwMjY0OdIBIWh0dHBzOi8vbWRwci5qcC9tdXNpYy9hbXAvMjUwMjY0OQ?oc=5',
                               'text': '関ジャニ∞が、丸山隆平と小島瑠璃子がMCを務める情報番組『サタデープラス』（MBS・TBS系／毎週土曜あさ7時30分～）のテーマソングを歌うことが決定した。',
                               'fallback': 'モデルプレス - ライフスタイル・ファッションエンタメニュース: 関ジャニ∞「サタデープラス」テーマソングを担当 - モデルプレス',
                               'image_url': 'https://img-mdpr.freetls.fastly.net/article/e_4H/nm/e_4Hq8NBsDfpKHelV29ylgnFVc0ZB6LWpR-xJZGxOZM.jpg?width=700&disable=upscale&auto=webp',
                               'from_url': 'https://news.google.com/__i/rss/rd/articles/CBMiJGh0dHBzOi8vbWRwci5qcC9tdXNpYy9kZXRhaWwvMjUwMjY0OdIBIWh0dHBzOi8vbWRwci5qcC9tdXNpYy9hbXAvMjUwMjY0OQ?oc=5',
                               'image_width': 375, 'image_height': 250, 'image_bytes': 84203,
                               'service_icon': 'https://mdpr.jp/favicon.ico', 'id': 2,
                               'original_url': 'https://news.google.com/__i/rss/rd/articles/CBMiJGh0dHBzOi8vbWRwci5qcC9tdXNpYy9kZXRhaWwvMjUwMjY0OdIBIWh0dHBzOi8vbWRwci5qcC9tdXNpYy9hbXAvMjUwMjY0OQ?oc=5'}],
                                  'edited': {'user': 'B0172NV7KNK', 'ts': '1616808935.000000'},
                                  'ts': '1616808935.012600'}, 'channel': 'C01R70X7CGG',
                      'previous_message': {'type': 'message', 'subtype': 'bot_message',
                                           'text': '<https://news.google.com/__i/rss/rd/articles/CBMiMGh0dHBzOi8vbmV3cy5teW5hdmkuanAvYXJ0aWNsZS8yMDIxMDMyNy0xODQ2NzI5L9IBAA?oc=5|関ジャニ∞、『サタデープラス』テーマソング歌う! 丸山隆平「想いを込めて」 - マイナビニュース>\n<https://news.google.com/__i/rss/rd/articles/CBMiMGh0dHBzOi8vbmV3cy5teW5hdmkuanAvYXJ0aWNsZS8yMDIxMDMyNy0xODQ2NzI5L9IBAA?oc=5|関ジャニ∞、『サタデープラス』テーマソング歌う! 丸山隆平「想いを込めて」>\xa0\xa0マイナビニュース<https://news.google.com/__i/rss/rd/articles/CBMiJGh0dHBzOi8vbWRwci5qcC9tdXNpYy9kZXRhaWwvMjUwMjY0OdIBIWh0dHBzOi8vbWRwci5qcC9tdXNpYy9hbXAvMjUwMjY0OQ?oc=5|関ジャニ∞「サタデープラス」テーマソングを担当>\xa0\xa0モデルプレス&lt;a...',
                                           'ts': '1616808935.012600', 'username': 'トップニュース - Google ニュース', 'icons': {
                              'image_36': 'https://a.slack-edge.com/80588/img/services/rss_36.png',
                              'image_48': 'https://a.slack-edge.com/80588/img/services/rss_48.png',
                              'image_72': 'https://a.slack-edge.com/80588/img/services/rss_72.png'},
                                           'bot_id': 'B0172NV7KNK'}, 'event_ts': '1616808935.012700',
                      'ts': '1616808935.012700', 'channel_type': 'channel'}, 'type': 'event_callback',
            'event_id': 'Ev01SHJS0XK7', 'event_time': 1616808935
            }
    req = Mock(get_json=Mock(return_value=data), args=data)
    res = slack_to_reddit(req)
    assert 'success' in res, f"no 'success' in res: {res}"


def test_slack_to_reddit_if_error():
    data = {'event': 'broken data boo!'}
    req = Mock(get_json=Mock(return_value=data), args=data)
    res = slack_to_reddit(req)
    assert 'success' in res and res['success'] == False, f"{res}"


if __name__ == '__main__':
    unittest.main()
