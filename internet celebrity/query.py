import json
import logging
import random
from datetime import timedelta, date
from multiprocessing.pool import Pool
import requests
from fake_useragent import UserAgent
from tweet import Tweet

ua = UserAgent()
HEADERS_LIST = [ua.chrome, ua.google, ua['google chrome'], ua.firefox, ua.ff]
INIT_URL = "https://twitter.com/{q}?lang=en"
#INIT_URL = "https://twitter.com/search?l=en&f=tweets&vertical=default&q={q}"
RELOAD_URL = "https://twitter.com/i/search/timeline?l=en&f=tweets&vertical=" \
             "default&include_available_features=1&include_entities=1&" \
             "reset_error_state=false&src=typd&max_position={pos}&q={q}"

def query_single_page(url, html_response=True, retry=3):

    headers = {'User-Agent': random.choice(HEADERS_LIST)}

    try:
        response = requests.get(url, headers=headers)
        if html_response:
            html = response.text
            urls = Tweet.from_html(html)
        else:
            json_resp = response.json()
            html = json_resp['items_html']
            urls = Tweet.from_html(html)
        tweets = list(Tweet.from_html(html))

        #print(urls)

        if not tweets:
            return [], None

        if not html_response:
            return tweets, json_resp['min_position']

        return tweets, "TWEET-{}-{}".format(tweets[-1].id, tweets[0].id)
    except requests.exceptions.HTTPError as e:
        logging.exception('HTTPError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.ConnectionError as e:
        logging.exception('ConnectionError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.Timeout as e:
        logging.exception('TimeOut {} while requesting "{}"'.format(
            e, url))
    if retry > 0:
        logging.info("Retrying...")
        return query_single_page(url, html_response, retry-1)

    logging.error("Giving up.")
    return [], None


def query_tweets_once(query, limit=None, num_tweets=0):

    logging.info("Querying {}".format(query))
    #query = query.replace(' ', '%20').replace("#", "%23").replace(":", "%3A")
    pos = None
    tweets = []

    try:
        while True:
            new_tweets, pos = query_single_page(
                INIT_URL.format(q=query) if pos is None
                else RELOAD_URL.format(q=query, pos=pos),
                pos is None
            )

            if len(new_tweets) == 0:
                logging.info("Got {} tweets for {}.".format(
                    len(tweets), query))
                return tweets

            logging.info("Got {} tweets ({} new).".format(
                len(tweets) + num_tweets, len(new_tweets)))

            tweets += new_tweets

            if limit is not None and len(tweets) + num_tweets >= limit:
                return tweets
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Returning tweets gathered "
                     "so far...")
    except BaseException:
        logging.exception("An unknown error occurred! Returning tweets "
                          "gathered so far.")

    return tweets


def eliminate_duplicates(iterable):

    class NoElement: pass

    prev_elem = NoElement
    for elem in sorted(iterable):
        if prev_elem is NoElement:
            prev_elem = elem
            yield elem
            continue

        if prev_elem != elem:
            prev_elem = elem
            yield elem


def query_tweets(query, limit=None):
    tweets = []
    iteration = 1

    while limit is None or len(tweets) < limit:

        logging.info("Running iteration no {}, query is {}".format(
            iteration, repr(query)))
        new_tweets = query_tweets_once(query, limit, len(tweets))
        tweets.extend(new_tweets)

        if not new_tweets:
            break

        mindate = min(map(lambda tweet: tweet.timestamp, new_tweets)).date()
        maxdate = max(map(lambda tweet: tweet.timestamp, new_tweets)).date()
        logging.info("Got tweets ranging from {} to {}".format(
            mindate.isoformat(), maxdate.isoformat()))

        if mindate != maxdate:
            mindate += timedelta(days=1)

        # Twitter will always choose the more restrictive until:
        query += ' until:' + mindate.isoformat()
        iteration += 1

        print("length of raw tweets: " + str(len(tweets)))

    # remove redundancy if scraped tweets surpass limits
    if len(tweets) > limit:
        redun = len(tweets) - limit
        for i in range(redun):
            del tweets[-1]
    print("length of new tweets: " + str(len(tweets))+"\n")

    # Eliminate duplicates
    # return list(eliminate_duplicates(tweets))
    return tweets


def query_all_tweets(query):

    year = 2006
    month = 3

    limits = []
    while date(year=year, month=month, day=1) < date.today():
        nextmonth = month + 1 if month < 12 else 1
        nextyear = year + 1 if nextmonth == 1 else year

        limits.append(
            (date(year=year, month=month, day=1),
             date(year=year, month=month, day=10))
        )
        limits.append(
            (date(year=year, month=month, day=10),
             date(year=year, month=month, day=20))
        )
        limits.append(
            (date(year=year, month=month, day=20),
             date(year=nextyear, month=nextmonth, day=1))
        )
        year, month = nextyear, nextmonth

    queries = ['{} since:{} until:{}'.format(query, since, until)
               for since, until in reversed(limits)]

    pool = Pool(20)
    all_tweets = []
    try:
        for new_tweets in pool.imap_unordered(query_tweets_once, queries):
            all_tweets.extend(new_tweets)
            logging.info("Got {} tweets ({} new).".format(
                len(all_tweets), len(new_tweets)))
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Returning all tweets "
                     "gathered so far.")

    return sorted(all_tweets)
