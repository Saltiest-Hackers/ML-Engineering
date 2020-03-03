import re
import typing
from decouple import config
import pandas as import pd
import numpy as np
import psycopg2
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

analyzer = SentimentIntensityAnalyzer()

def escape_string(text):
    if isinstance(text, str):
        text = re.sub(r"\"", "\\\"", text)
        text = re.sub(r"'", "\\'", text)
        return text
    else:
        return "-"

def convert_int(x):
    try:
        return int(x)
    except:
        return -1

def get_saltiness(x):
    if isinstance(x, str):
        res = analyzer.polarity_scores(x)["neg"]
        return res
    return 0.0

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
