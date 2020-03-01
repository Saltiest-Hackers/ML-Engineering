#!/bin/bash
# Collect most recent post from Hacker News API

echo "*** DETERMINING ID OF MOST RECENT HACKER NEWS POST ***"

wget https://hacker-news.firebaseio.com/v0/maxitem.json -O latest.postId
MIN_ID=1
MAX_ID=$(cat ./latest.postId)

for ((x=$MIN_ID; x<$MAX_ID; x++))
do
    # append a uri for the current id to the file
    echo "https://hacker-news.firebaseio.com/v0/item/$x.json" >> hn-uri.txt
    if ! ((x % 10000)); then
        echo current id $x
    fi
done