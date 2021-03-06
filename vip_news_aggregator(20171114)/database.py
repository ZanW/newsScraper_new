import re
import time
import newspaper
import pymysql
import requests
from newspaper import Article
from query import query_tweets

host = "127.0.0.1"
password = "root"
user = "root"
database = "news"

class Database:

    @classmethod
    def set_raw(cls, v_name, temp, H_url, title, news_text, re_tweet, like):


        # store timestamp, url, title, text into table 'newsinfo' in database 'twitternews'
        conn = pymysql.connect(host=host, user=user, passwd=password, db=database)

        # use re.compile to remove all except things kept in []
        for i in range(len(temp)):
            try:

                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]
                Tretweet = re_tweet[i]
                Tlikes = like[i]

                sql = "insert into vip_news(v_name, posted_time, title, URL, text, fwd_fre, likes) values('" + v_name + "','" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "','" + Tretweet + "','" + Tlikes + "')"
                conn.query(sql)

            except:
                #print("sql error")
                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]
                Tretweet = re_tweet[i]
                Tlikes = like[i]

                regex = re.compile('[^a-zA-Z0-9\,\.\s]')
                TTitle = regex.sub('', TTitle)
                if isinstance(TText, str):
                    TText = regex.sub('', TText)
                else:
                    TText = ""
                # add quotation to text start and end
                TText = "'''" + TText + "'''"

                # insert into database after adding new quotation
                try:
                    sql = "insert into vip_news(v_name, posted_time, title, URL, text, fwd_fre, likes) values('" + v_name + "','" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "','" + Tretweet + "','" + Tlikes + "')"
                    conn.query(sql)
                except :
                    sql = "insert into vip_news(v_name, posted_time, title, URL, text, fwd_fre, likes) values('" + v_name + "','" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + "N/A" + "','" + Tretweet + "','" + Tlikes + "')"
                    conn.query(sql)

        conn.close()


def search_task(V_name, l):
    print("search_task starts")
    tim = []
    short_url = []
    docker = []  # docker to store results of query_tweets for one search
    title = []
    re_tweet = []
    like = []

    # if StartDay != 0 and EndDay != 0 and StartDay < EndDay:
    # for i in range(x, y):
    for tweet in query_tweets(V_name, l)[:l]:
        re_tweet.append(tweet.retweets)
        like.append(tweet.likes)
        short_url.append(tweet.url)
        docker.append(tweet)
        text = tweet.text.encode('utf-8').decode('utf-8')
        text = text.replace('\n', '')
        text = re.sub(r'http\S+.*[\r\n]*', '', text, flags=re.MULTILINE)
        title.append(text)
        tim.append(tweet.timestamp)

    for i in range(len(docker)):
        for j in range(i + 1, len(docker)):
            if docker[i].timestamp.timetuple()[4] < docker[j].timestamp.timetuple()[4]:
                temp = docker[i]
                docker[i] = docker[j]
                docker[j] = temp
            elif (docker[i].timestamp.timetuple()[4] == docker[j].timestamp.timetuple()[4]) and (
                docker[i].timestamp.timetuple()[5] < docker[j].timestamp.timetuple()[5]):
                temp = docker[i]
                docker[i] = docker[j]
                docker[j] = temp

    timeStr = [[] for l in range(len(docker))]

    for i in range(len(docker)):
        for j in range(6):
            timeStr[i].append(str(docker[i].timestamp.timetuple()[j]))
            if j <= 2:
                timeStr[i].append("/")
            elif j != 5:
                timeStr[i].append(":")
            else:
                break

    temp = []
    for i in range(len(docker)):
        temp.append(''.join(timeStr[i]))

    timeStamp_FM = [[] for i in range(len(timeStr))]
    for i in range(len(temp)):
        timeStamp_FM[i].append(temp[i])

    # short_url = short_url[::-1]

    TupleList1 = []
    for i in range(len(docker)):
        TupleList1.append((temp[i], docker[i].text.encode('utf-8').decode('utf-8')))

    TupleList2 = []
    for i in range(len(docker)):
        TupleList2.append((temp[i], short_url[i]))

    assort1 = dict()
    for i in range(len(TupleList1)):
        if TupleList1[i][0] in assort1:
            assort1[TupleList1[i][0]].append(TupleList1[i][1])
        else:
            assort1[TupleList1[i][0]] = [TupleList1[i][1]]

    assort2 = dict()
    for i in range(len(TupleList2)):
        if TupleList2[i][0] in assort2:
            assort2[TupleList2[i][0]].append(TupleList2[i][1])
        else:
            assort2[TupleList2[i][0]] = [TupleList2[i][1]]  # [TupleList[i][1]] here guarantees

    resp = []
    H_url = []
    session = requests.Session()  # so connections are recycled
    news_title = 0
    for url in short_url:
        print(str((news_title + 1)) + " news from VIP have been scraped")
        print("VIP Name:" + V_name)
        print("News Title: " + title[news_title])
        print("News forwarded times: " + re_tweet[news_title])
        print("News likes:" + like[news_title])
        # print(url)
        if url != "None":
            H_url.append("http://" + url)
            print("http://" + url + "\n")
        else:
            H_url.append("No URL found in this tweet")
            print("No URL found in this tweet\n")
        try:
            resp.append(session.head("http://" + url, allow_redirects=True))
        except:
            resp.append("error")
        news_title += 1

    news_text = []
    text_cont = 0
    for r in H_url:
        print("sleep starts...")
        time.sleep(1)
        print("sleep completes...\n")
        try:
            article = Article(r)
            try:
                article.download()
            except:
                pass
            article.parse()
            if len(article.text) == 0:
                news_text.append("No News to Scrape")
            else:
                news_text.append(article.text)
        except newspaper.article.ArticleException as e:
            news_text.append(e)
        text_cont += 1
        print(str(text_cont) + " news text have been scraped")

    TupleList3 = []
    for i in range(len(docker)):
        TupleList3.append((temp[i], news_text[i]))

    assort3 = dict()
    for i in range(len(TupleList3)):
        if TupleList3[i][0] in assort3:
            assort3[TupleList3[i][0]].append(TupleList3[i][1])

        else:
            assort3[TupleList3[i][0]] = [TupleList3[i][1]]  # [TupleList[i][1]] here guarantees

    # create dictionary as for title-Timestamp, title-url, title-text
    Title_Time = []
    for i in range(len(docker)):
        Title_Time.append((title[i], temp[i]))

    dict_tt = dict()
    for i in range(len(Title_Time)):  # Num of Title_Time equals that of dockers
        if Title_Time[i][0] in dict_tt:
            dict_tt[Title_Time[i][0]].append(Title_Time[i][1])
        else:
            dict_tt[Title_Time[i][0]] = [Title_Time[i][1]]

    Title_Url = []
    for i in range(len(docker)):
        Title_Url.append((title[i], H_url[i]))

    dict_tu = dict()
    for i in range(len(Title_Url)):  # Num of Title_Time equals that of dockers
        dict_tu[Title_Url[i][0]] = [Title_Url[i][1]]

    Title_Text = []
    for i in range(len(docker)):
        Title_Text.append((title[i], news_text[i]))

    dict_tx = dict()
    for i in range(len(Title_Text)):  # Num of Title_Time equals that of dockers
        dict_tx[Title_Text[i][0]] = [Title_Text[i][1]]

    # database operation
    if not title:
        print("No news available within the searching time window")

    else:
        print("database operation starts\n")
        # Database.clear_table()

        # write raw data to database newinfo_raw
        Database.set_raw(V_name, temp, H_url, title, news_text, re_tweet, like)

        print("raw data write into database complete\n")

    return

if __name__ == '__main__':
    pass
