import json
import logging
import traceback
from datetime import datetime
from typing import Optional
from urllib.request import urlopen

from dict_digger import dig


def ia_oldest_available_url(url: str) -> Optional[datetime]:
    # wayback machineからキャッシュURLを取得する
    try:
        query = [
            "http://archive.org/wayback/available",
            "?url=" + url,
            "&timestamp=19700101000000",  # 古い順に見たいのでUNIX timeの最古を指定
        ]

        json_str = urlopen(''.join(query)).read().decode('utf-8')
        resp_dict = json.loads(json_str)
        logging.debug(resp_dict)
        ts = dig(resp_dict, "archived_snapshots", "closest", "timestamp")
        if ts:
            # ts = '20210115032718' <-- YYYYmmddHHMMSS
            return datetime.strptime(ts, '%Y%m%d%H%M%S')
    except Exception:
        logging.error(f"failed to access ia, query: {query}")
        logging.error(traceback.format_exc())

    return None


def ia_available_url(url: str, ts: datetime) -> Optional[str]:
    # wayback machineからキャッシュURLを取得する
    try:
        query = [
            "http://archive.org/wayback/available",
            f"?url={url}",
            f"&timestamp={ts.strftime('%Y%m%d%H%M%S')}",
        ]

        json_str = urlopen(''.join(query)).read().decode('utf-8')
        resp_dict = json.loads(json_str)
        logging.debug(resp_dict)
        archive_url = dig(resp_dict, "archived_snapshots", "closest", "url")
        if archive_url:
            return archive_url
    except Exception:
        logging.error(traceback.format_exc())

    return None
