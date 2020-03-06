import utils
from config import *

import requests
import re
import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd
import nltk

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()


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

def refine(df):

    df = df.loc[df['type'] == 'comment']
    df = df.loc[df['author'].isnull() == False]
    df = df[['id', 'time', 'author', 'parent', 'text', 'type']]
    df['parent'] = df['parent'].astype(int)
    return df

def scrub(doc):
    patt = {
            "unicode_patt": "&.{4}(?=;);",
            "line_break":   "<p>",
            "href_patt":    "<a.*</a>",
            "quote":        "&quot;",
            "html_footnote": "\[.\]",
            "punctuation":   "[^\w\s]",
            "numbers":       "[^A-Za-z\s]",
        }

    r = rf'|'.join(patt.values())
    return re.sub(r, ' ', str(doc))

def process_text(df):

    # regex
    df['processed_text'] = df['text'].apply(scrub)
    # lowercase
    df['processed_text'] = df['processed_text'].str.lower()
    # double spaces
    df['processed_text'] = df['processed_text'].str.replace(r'\s+', ' ')


    # word freq
    word_freq = pd.Series(' '.join(df['processed_text']).split()).value_counts()

    common = list(word_freq[:10].index)
    rare = list(word_freq[word_freq.values < 2].index)

    stop_words = list(nltk.corpus.stopwords.words('english'))
    stop_words = set(stop_words + common + rare)

    print('removing stopwords')
    pat = r'\b(?:{})\b'.format('|'.join(stop_words))

    df['no_stopwords'] = df['processed_text'].str.replace(pat, '')
    df['no_stopwords'] = df['no_stopwords'].str.replace(r'\s+', ' ')

    # remove less than 2 words
    df = df[df["no_stopwords"].str.split(" ").apply(lambda x: len(x)) > 3]

    return df


with psycopg2.connect(CONN_ARGS) as conn:
    with conn.cursor() as curs:

        # Collect id of most recent post in DB
        query = """
            SELECT id
            FROM comments
            ORDER BY id desc
            LIMIT 1;
        """
        curs.execute(query)
        response = curs.fetchone()

        # collect recent posts from Hacker News API

        min_id = response[0] + 1
        max_id = requests.get(LATEST).json()

        df = utils.retrieve_posts(min_id, max_id)
        df = process_text(df)
        
        cols = list(df.columns)
        id_col = cols.index("id")
        by_col = cols.index("by")
        time_col = cols.index("time")
        text_col = cols.index("text")
        parent_col = cols.index("parent")


        batch = [
            [
                row[1][id_col],
                row[1][by_col],
                row[1][time_col],
                row[1][text_col],
                row[1][parent_col],
                get_saltiness(row[1][text_col]),
            ]
            for row in df.iterrows()
        ]

        batch = [
            row for row in batch if row[-1] < 1.0
        ]


        query = """
            INSERT INTO comments (id, author, time, comment_text, parent_id, saltiness)
            VALUES (%s, %s, %s, %s, %s, %s);
        """

        execute_batch(curs, query, batch)

    conn.commit()
