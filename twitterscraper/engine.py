from twitterscraper.query import query_tweets
from twitterscraper.tweet import Tweet
import pymysql
import re
from string import digits
from datetime import datetime
from collections import OrderedDict
from newspaper import Article
import requests
import string

# set x to start date, set y to end date,
# note x < y, (x,y must be 1 digit)
x = 26
y = 27

# set m to month(if 1 digit, place 0 before it. e.g: May is 05)
m = 9

# set l to No. of news to scrape(l >= 1)
l = 5

# set keyword for searching
keyword = "bitcoin"

time = []
short_url = []
# docker to store results of query_tweets for one search
docker = []
title = []

if x != 0 and y != 0 and len('x') == 1 and len('y') == 1:
    for i in range(x, y):
        for tweet in query_tweets(keyword + " since%3A2017-{}-0{} until%3A2017-{}-0{}".format(m, x, m, y), l)[:l]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')
            #text = tweet.text.encode('utf-8')
            text = re.sub(r"http\s+", "", text)
            title.append(text)
            #testdata = text.encode('utf-8')
            time.append(tweet.timestamp)
            if x == y: break

elif x != 0 and y != 0 and len('x') == 1 and len('y') == 2:
    for i in range(x, y):
        for tweet in query_tweets(keyword + " since%3A2017-{}-0{} until%3A2017-{}-{}".format(m, x, m, y), l)[:l]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')
            #text = tweet.text.encode('utf-8')
            text = re.sub(r"http\s+", "", text)
            title.append(text)
            #testdata = text.encode('utf-8')
            time.append(tweet.timestamp)
            if x == y: break

# current date by default
elif x == 0 and y == 0:
    for tweet in query_tweets(keyword, l)[:l]:
        short_url.append(tweet.url)
        docker.append(tweet)
        text = tweet.text.encode('utf-8').decode('utf-8') # decode() removes binary mark: b'
        #text = tweet.text.encode('utf-8')
        text = re.sub(r"http\s+", "", text)
        title.append(text)
        #testdata = text.encode('utf-8')
        time.append(tweet.timestamp)
#        if x == y: break

elif x != 0 and y != 0 and len('x') == 2 and len('y') == 2:
    for i in range(x, y):
        for tweet in query_tweets(keyword + " since%3A2017-{}-{} until%3A2017-{}-{}".format(m, x, m, y), l)[:l]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')
            #text = tweet.text.encode('utf-8')
            text = re.sub(r"http\s+", "", text)
            title.append(text)
            #testdata = text.encode('utf-8')
            time.append(tweet.timestamp)
            if x == y: break


# compare timestamp in docker(compare min firstly, sec secondly), sorted in descending order
for i in range(len(docker)):
    for j in range(i + 1, len(docker)):
        if docker[i].timestamp.timetuple()[4] < docker[j].timestamp.timetuple()[4]:
            temp = docker[i]
            docker[i] = docker[j]
            docker[j] = temp
        elif (docker[i].timestamp   .timetuple()[4] == docker[j].timestamp.timetuple()[4]) and (docker[i].timestamp.timetuple()[5] < docker[j].timestamp.timetuple()[5]):
            temp = docker[i]
            docker[i] = docker[j]
            docker[j] = temp

timeStr = [[] for l in range(len(docker))]

#for i in range(len(locker)):
# get year,month, divide by "/"
# get hour,minute,second, divide by ":"
for i in range(len(docker)):
    for j in range(6):
        timeStr[i].append(str(docker[i].timestamp.timetuple()[j]))
        if j <= 2:
            timeStr[i].append("/")
        elif j != 5:
            timeStr[i].append(":")
        else: break

temp = []
for i in range(len(docker)):
    temp.append(''.join(timeStr[i]))

# create nested list timeStamp_FM to accommodate formalized timeStamp
timeStamp_FM = [[] for i in range(len(timeStr))]
for i in range(len(temp)):
    timeStamp_FM[i].append(temp[i])

short_url = short_url[::-1] # reverse urls

# create (timestamp,text) tuples in one list: text here contains title, url
TupleList1 = []
for i in range(len(docker)):
    TupleList1.append((temp[i], docker[i].text.encode('utf-8').decode('utf-8')))

# create (timestamp,shortURL) tuples in one list
TupleList2 = []
for i in range(len(docker)):
    TupleList2.append((temp[i], short_url[i]))

# dict Tuplelist1(timestamp,text): text here contains title, url
assort1 = dict()
for i in range(len(TupleList1)): # Num of Touplist equals that of dockers
    if TupleList1[i][0] in assort1:
        assort1[TupleList1[i][0]].append(TupleList1[i][1])
    else:
        assort1[TupleList1[i][0]] = [TupleList1[i][1]] # [TupleList[i][1]] here guarantees one key gives one list

# dict Tuplelist1(timestamp,shortURL)
assort2 = dict()
for i in range(len(TupleList2)):  # Num of Touplist equals that of dockers
    if TupleList2[i][0] in assort2:
        assort2[TupleList2[i][0]].append(TupleList2[i][1])
    else:
        assort2[TupleList2[i][0]] = [TupleList2[i][1]]  # [TupleList[i][1]] here guarantees




# regain longURL from Short URL, store longURL in resp[]
resp = []
H_url = [] # "http://" + "short_url"
session = requests.Session()  # so connections are recycled

for url in short_url:
    try:
        print("http://" + url)
        H_url.append("http://" + url)
        resp.append(session.head("http://" + url, allow_redirects=True))
    except: resp.append("error")

'''
# mining news from corresponding longURL; store news texts in text[]
news_text = []
for r in resp:
    try:
        if isinstance(r, str):
            news_text.append("Null")
        else:
            article = Article(r.url)
            article.download()
            article.parse()
            news_text.append(article.text)
    except: news_text.append("Error")
'''

# mining news from "http:// + short_url"; store news texts in text[]
news_text = []
for r in H_url:
    try:
        article = Article(r)
        article.download()
        article.parse()
        news_text.append(article.text)
    except:
        news_text.append("Error")


# create (timestamp,news_text) tuples in one list
TupleList3 = []
for i in range(len(docker)):
    TupleList3.append((temp[i], news_text[i]))

# dict Tuplelist3(timestamp,news_text)
assort3 = dict()
for i in range(len(TupleList3)):  # Num of Touplist equals that of dockers
    if TupleList3[i][0] in assort3:
        assort3[TupleList3[i][0]].append(TupleList3[i][1])
    else:
        assort3[TupleList3[i][0]] = [TupleList3[i][1]]  # [TupleList[i][1]] here guarantees


#inOrder = OrderedDict(assort)

# store timestamp, url, title, text into table 'newsinfo' in database 'twitternews'
conn = pymysql.connect(host = "127.0.0.1", user = "root", passwd = "root", db = "twitternews")

'''
# add try...except
for i in range(len(temp)):
    try:
        TmStamp = temp[i]
        HUrl = H_url[i]
        TTitle = title[i]
        TText = news_text[i].decode()
        TText = TText.replace("'", " ")
        TText = TText.replace('"', ' ')

        print("*********************************************")
        print(TmStamp)
        print(HUrl)
        print(TTitle)
        print(TText)
        print("*********************************************")

        #sql = "insert into newsinfo(Tstamp, Title, URL, Texts) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "')"
        sql = "insert into newsinfo(Tstamp, Title, URL, Texts) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "')"

        conn.query(sql)
    except:
        print("sql error")
        sql = "insert into newsinfo(Tstamp, Title, URL, Texts) values('N/A', 'N/A', 'N/A', 'N/A')"
        conn.query(sql)

'''


for i in range(len(temp)):

    TmStamp = temp[i]
    HUrl = H_url[i]
    TTitle = title[i]
    TText = news_text[i]

    # remove punctuation in TText
    exclude = set(string.punctuation)
    TText = ''.join(ch for ch in TText if ch not in exclude)
    TText = TText.replace("'", "")
    TText = TText.replace("-", "")
    TText = TText.replace('"', '')
    TText = TText.replace("’", "")
    TText = TText.replace("”", "")
    TText = TText.replace("“", "")
    TText = TText.replace("‘", "")
    #TText = "'''" + TText + "'''"
    print(len(TText))

    # remove punctuation in TTitle
    exclude = set(string.punctuation)
    TTitle = ''.join(ch for ch in TTitle if ch not in exclude)
    TTitle = TTitle.replace("'", "")
    TTitle = TTitle.replace("-", "")
    TTitle = TTitle.replace('"', '')
    TTitle = TTitle.replace("’", "")
    TTitle = TTitle.replace("”", "")
    TTitle = TTitle.replace("“", "")
    TTitle = TTitle.replace("‘", "")

    print("*********************************************")
    print(TmStamp)
    print(HUrl)
    print(TTitle)
    print(TText)
    print("*********************************************")

    #sql = "insert into newsinfo(Tstamp, Title, URL, Texts) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "')"
    sql = "insert into newsinfo(Tstamp, Title, URL, Texts) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "')"

    conn.query(sql)

conn.close()



print(assort1)
print(len(assort1))
#print(assort2)
#print(assort3)
#print(len(assort3))
print(H_url)
print(len(H_url))
print(temp)
print(len(temp))
print(title)
print(len(title))
print(news_text)
print(len(news_text))
