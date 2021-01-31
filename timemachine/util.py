from typing import Pattern, Optional, Tuple


def find_item_recursive(obj: dict, key_r: Pattern) -> Optional[Tuple[str, str]]:
    matched_keys = list(filter(key_r.match, obj.keys()))
    if len(matched_keys) > 0:
        key: str = matched_keys[0]
        return key, obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = find_item_recursive(obj=v, key_r=key_r)
            if item is not None:
                return item
    return None