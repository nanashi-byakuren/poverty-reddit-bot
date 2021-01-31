import json
import logging
import traceback
from datetime import datetime
from typing import Optional
from urllib.request import urlopen

from dict_digger import dig


def get_ia_available_url(url: str) -> Optional[datetime]:
    # wayback machineからキャッシュURLを取得する
    try:
        query = [
            "http://archive.org/wayback/available",
            "?url=" + url,
        ]

        json_str = urlopen(''.join(query)).read().decode('utf-8')
        resp_dict = json.loads(json_str)
        logging.debug(resp_dict)
        ts = dig(resp_dict, "archived_snapshots", "closest", "timestamp")
        if ts:
            return datetime.fromtimestamp(int(ts))
    except Exception:
        logging.error(f"failed to access ia, query: {query}")
        logging.error(traceback.format_exc())

    return None