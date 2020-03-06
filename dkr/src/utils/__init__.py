import pandas as pd
import requests
from config import *

LIMIT = 100

def retrieve_posts(start: int, stop: int):
    """Collects new posts from hacker news api

    Args:
    -----
    start - int - id of first post to collect
    stop - int - id of last post to collect

    Returns:
    -------
    posts - pd.Dataframe
    """
    if start > stop:
        raise ValueError("Value mismatch: Start must be less than stop")

    new_items = list(range(start, stop + 1))

    comments = []
    count = 0

    for uri in new_items:
        uri = HNAPI + f'item/{uri}.json'
        print(f"Getting post: {uri}")
        item = requests.get(uri).json()

        if item is None:
            continue

        comment = True if item['type'] == 'comment' else False
        if not comment:
            continue

        comments.append(item)

        count += 1
        if count >= LIMIT:
            break

    return pd.DataFrame(comments)
