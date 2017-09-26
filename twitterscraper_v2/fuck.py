from twitterscraper.query import query_tweets
from twitterscraper.tweet import Tweet

import re
from string import digits
from datetime import datetime
from collections import OrderedDict

for tweet in query_tweets("bitcoin", 10)[:10]:
    text = tweet.user.encode('utf-8')
    url = tweet.url
    print(text)
    print(url)

print("--------------------")