from decouple import config



# Hacker News API
HNAPI = "https://hacker-news.firebaseio.com/v0/"
LATEST = HNAPI + "maxitem.json"


# Postgres DB config
USERNAME = config("POSTGRES_USERNAME") 
PASSWORD = config("POSTGRES_PASSWORD")

CONN_ARGS = ("postgres://" +\
        USERNAME + ":" + PASSWORD + \
            "@raja.db.elephantsql.com:5432/mozfsrjp")

