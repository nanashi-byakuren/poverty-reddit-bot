from datetime import datetime

from timemachine.ia import ia_oldest_available_url


def test_ia_oldest_available_url():
    res = ia_oldest_available_url('https://www.news24.jp/articles/2020/01/29/07586221.html')
    assert res == datetime.strptime('2020-01-29 16:11:18', '%Y-%m-%d %H:%M:%S')
