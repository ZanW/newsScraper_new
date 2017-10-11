import re
import time
import pymysql
import requests
from newspaper import Article

from twitterscraper.similarity import Similarity

from twitterscraper.database import Database

from twitterscraper.query import query_tweets

# set x to start date, set y to end date,
# note x < y, (x,y must be less than 2 digit)
# x = 0, y = 0 get latest news
x = 0
y = 0

# set m to month(if 1 digit, place 0 before it. e.g: May is 05)
m = 10

# set l to No. of news to scrape(l >= 1)
l = 1000

# set keyword for searching
keyword = "bitcoin"

tim = []
short_url = []
# docker to store results of query_tweets for one search
docker = []
title = []

# "text" contains title & url information
if x != 0 and y != 0 and len('x') == 1 and len('y') == 1:
    for i in range(x, y):
        for tweet in query_tweets(keyword + " since%3A2017-{}-0{} until%3A2017-{}-0{}".format(m, x, m, y), l)[:l]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')
            #text = tweet.text.encode('utf-8')
            text = text.replace('\n', '')
            text = re.sub(r'http\S+.*[\r\n]*', '', text, flags=re.MULTILINE)
            title.append(text)
            #testdata = text.encode('utf-8')
            tim.append(tweet.timestamp)
            if x == y: break

elif x != 0 and y != 0 and len('x') == 1 and len('y') == 2:
    for i in range(x, y):
        for tweet in query_tweets(keyword + " since%3A2017-{}-0{} until%3A2017-{}-{}".format(m, x, m, y), l)[:l]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')
            #text = tweet.text.encode('utf-8')
            text = text.replace('\n', '')
            text = re.sub(r'http\S+.*[\r\n]*', '', text, flags=re.MULTILINE)
            title.append(text)
            #testdata = text.encode('utf-8')
            tim.append(tweet.timestamp)
            if x == y: break

# current date by default
elif x == 0 and y == 0:
    for tweet in query_tweets(keyword, l)[:l]:
        short_url.append(tweet.url)
        docker.append(tweet)
        text = tweet.text.encode('utf-8').decode('utf-8') # decode() removes binary mark: b'
        #text = tweet.text.encode('utf-8')
        text = text.replace('\n', '')
        text = re.sub(r'http\S+.*[\r\n]*', '', text, flags=re.MULTILINE)
        title.append(text)
        #testdata = text.encode('utf-8')
        tim.append(tweet.timestamp)
        #if x == y: break

elif x != 0 and y != 0 and len('x') == 2 and len('y') == 2:
    for i in range(x, y):
        for tweet in query_tweets(keyword + " since%3A2017-{}-{} until%3A2017-{}-{}".format(m, x, m, y), l)[:l]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')
            #text = tweet.text.encode('utf-8')
            text = text.replace('\n', '')
            text = re.sub(r'http\S+.*[\r\n]*', '', text, flags=re.MULTILINE)
            title.append(text)
            #testdata = text.encode('utf-8')
            tim.append(tweet.timestamp)
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
news_title = 0
for url in short_url:
    try:
        print("http://" + url)
        H_url.append("http://" + url)
        resp.append(session.head("http://" + url, allow_redirects=True))
    except: resp.append("error")
    news_title += 1
    print(str(news_title) + " news titles have been scraped")

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
text_cont = 0
for r in H_url:

    print("sleep starts...")
    time.sleep(3) # avoid annoying twitter server, parse text every 2 seconds
    print("sleep complete...\n")

    try:
        article = Article(r)
        article.download()
        article.parse()
        news_text.append(article.text)
    except:
        news_text.append("Error")
    text_cont += 1
    print(str(text_cont) + " news text have been scraped")


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

############################################ create dict pair ############################################
# create dictionary as for title-Timestamp, title-url, title-text
# dict {title, timestamp}
Title_Time = []
for i in range(len(docker)):
    Title_Time.append((title[i], temp[i]))

dict_tt = dict()
for i in range(len(Title_Time)):  # Num of Title_Time equals that of dockers
    if Title_Time[i][0] in dict_tt:
        dict_tt[Title_Time[i][0]].append(Title_Time[i][1])
    else:
        dict_tt[Title_Time[i][0]] = [Title_Time[i][1]]

# dict {title, url}
Title_Url = []
for i in range(len(docker)):
    Title_Url.append((title[i], H_url[i]))

dict_tu = dict()
for i in range(len(Title_Url)):  # Num of Title_Time equals that of dockers
    #if Title_Url[i][0] in dict_tt:
        #dict_tu[Title_Url[i][0]].append(Title_Url[i][1])
    #else:
    dict_tu[Title_Url[i][0]] = [Title_Url[i][1]]

# dict {title, text}
Title_Text = []
for i in range(len(docker)):
    Title_Text.append((title[i], news_text[i]))

dict_tx = dict()
for i in range(len(Title_Text)):  # Num of Title_Time equals that of dockers
    #if Title_Text[i][0] in dict_tt:
        #dict_tx[Title_Text[i][0]].append(Title_Text[i][1])
    #else:
    dict_tx[Title_Text[i][0]] = [Title_Text[i][1]]


#################################### database operation starts #######################################
print("database operation starts\n")

# release database from old redundant data
Database.clear_table()

# write raw data to database newinfo_raw
Database.set_raw(temp, H_url, title, news_text)
print("raw data write into database complete\n")

# write raw data to database newinfo_simifre
TitleFrequency = Similarity.get_simi_titlefre(title) #invoke function in similarity class to get title-frequency after similariy screen

frequency_similarity = list(TitleFrequency.values()) # dict to list
title_similarity = list(TitleFrequency.keys()) # dict to list
Frequency_similarity = TitleFrequency.values()
Title_similarity = TitleFrequency.keys()
URL_similarity = [dict_tu[titl] for titl in Title_similarity]
TmStamp_similarity = [dict_tt[titl] for titl in Title_similarity]
Text_similarity = [dict_tx[titl] for titl in Title_similarity]

Database.set_simifre(TmStamp_similarity, URL_similarity, title_similarity, Text_similarity, frequency_similarity)
print("similarity screened data write into database complete\n")

#################################### database operation ends #######################################











