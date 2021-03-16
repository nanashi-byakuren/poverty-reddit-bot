import unittest
from unittest.mock import Mock

from slack_to_reddit.main import slack_to_reddit


def test_slack_to_reddit():
    data = {'type': 'url_verification', 'challenge': 'dummy'}
    req = Mock(get_json=Mock(return_value=data), args=data)
    assert slack_to_reddit(req) == {'challenge': 'dummy'}, "challenge not matched"


if __name__ == '__main__':
    unittest.main()
