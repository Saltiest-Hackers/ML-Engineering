import re
import typing
from decouple import config
import pandas as pd
import numpy as np
import psycopg
from vaderSentment.vaderSentiment import SentimentIntensityAnalyzer
import requests


def hit(endpoint):
    return requests.get(endpoint).json()

# TEXT PROCESSING
def escape_string(text):
    if isinstance(text, str):
        text = re.sub(r"\"", "\\\"", text)
        text = re.sub(r"'", "\\'", text)
        return text
    else:
        return "-"


analyzer = SentimentIntensityAnalyzer()

# INSERT NEW VALUES INTO TABLE
batchsize = 10000

for ix in range(0, len(hn_df)+1, batchsize):
    
    print(f"Batch {ix} / {len(hn_df)} -- {ix/len(hn_df)*100:.2f}%")
    
    batch = hn_df[ix:ix+batchsize]
    batch = [
        [
            row[1][1],
            row[1][2],
            row[1][3],
            row[1][4],
            convert_int(row[1][7]),
            get_saltiness(row[1][4]),
        ]
        for row in batch.iterrows()
    ]
    
    query = """
        INSERT INTO comments (id, author, time, comment_text, parent_id, saltiness)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    curs = conn.cursor()
    psycopg2.extras.execute_batch(curs, query, batch)
    curs.close()

conn.commit()
