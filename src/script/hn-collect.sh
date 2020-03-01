#!/bin/bash
cat hn-uri.txt | xargs -P 100 -n 100 wget --quiet