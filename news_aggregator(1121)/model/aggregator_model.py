import re
import time
import newspaper
import requests
from model.similarity import Similarity
from newspaper import Article
from model.query import query_tweets
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table

host = "127.0.0.1"
password = "root"
user = "root"
database = "news"

Base = declarative_base()

class NewinfoSimifre(Base):
    __tablename__ = 'newinfo_simifre'
    id = Column(Integer, primary_key=True)
    posted_time = Column(String, nullable=True)
    title = Column(String, nullable=True)
    URL = Column(String, nullable=True)
    text = Column(String, nullable=True)
    search_job_id = Column(Integer, nullable=True)
    similatiry_fre = Column(String, nullable=True)

    def toJSON(self):
        return {'Title': self.title,
                'URL': self.URL,
                'Text': self.text,
                'Similatiry_Fre': self.similatiry_fre,
                }


class SearchJob(Base):
    __tablename__ = 'search_job'
    id = Column(Integer, primary_key=True)
    keyword = Column(String, nullable=True)
    month = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    limit = Column(String, nullable=True)


class VIPNews(Base):
    __tablename__ = 'vip_news'
    id = Column(Integer, primary_key=True)
    v_name = Column(String(255), nullable=True)
    posted_time = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    URL = Column(String(255), nullable=True)
    text = Column(Text, nullable=True)
    fwd_fre = Column(Integer, nullable=True)
    likes = Column(Integer, nullable=True)

    def toJSON(self):
        return {'VIP_Name': self.v_name,
                'Posted_Time': self.posted_time,
                'Title': self.title,
                'URL': self.URL,
                'Fwd_Fre': self.fwd_fre,
                'Likes': self.likes,
                }


class Database:
    @classmethod
    def clear_table(self, table_name):
        # print("start to clear all information in tables :" + table_name+"\n")
        print("start to clear all information in tables " + table_name + "\n")
        engine = get_db()[2]
        meta = MetaData()
        meta.reflect(
            bind=engine)  # Automatically creates Table entries in this MetaData for any table available in the database but not yet present in the MetaData
        for table in reversed(meta.sorted_tables):
            if str(table) == table_name:
                print(str(table))
                engine.execute(table.delete())
        print("table clear completes\n")

    @classmethod
    def set_raw_all(cls, temp, H_url, title, news_text, search_job_id):
        # store timestamp, url, title, text into table 'newsinfo' in database 'twitternews'
        # conn = pymysql.connect(host=host, user=user, passwd=password, db=database)

        # use re.compile to remove all except things kept in []
        for i in range(len(temp)):
            try:

                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]

                TTitle = fix(TTitle)
                TText = fix_text1(TText)

                # get Table object and insert data
                meta = MetaData()
                engine = get_db()[2]
                connection = get_db()[1]
                newinfo_raw = Table('newinfo_raw', meta, autoload=True, autoload_with=engine)
                ins = newinfo_raw.insert()
                connection.execute(ins, posted_time=TmStamp, title=TTitle, URL=HUrl, search_job_id=str(
                    search_job_id), text=TText)

            except:
                print("sql error")

                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]

                TTitle = fix(TTitle)
                TText = fix_text1(TText)
                # add quotation to text start and end
                TText = "'''" + TText + "'''"

                # get Table object and insert data
                meta = MetaData()
                engine = get_db()[2]
                connection = get_db()[1]
                newinfo_raw = Table('newinfo_raw', meta, autoload=True, autoload_with=engine)
                ins = newinfo_raw.insert()
                connection.execute(ins, posted_time=TmStamp, title=TTitle, URL=HUrl, search_job_id=str(
                    search_job_id), text=TText)

    @classmethod
    def set_raw_vip(cls, v_name, temp, H_url, title, news_text, re_tweet, like):
        # store timestamp, url, title, text into table 'newsinfo' in database 'twitternews'
        # use re.compile to remove all except things kept in []
        for i in range(len(temp)):
            try:

                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]
                Tretweet = re_tweet[i]
                Tlikes = like[i]

                # get Table object and insert data
                meta = MetaData()
                engine = get_db()[2]
                connection = get_db()[1]
                vip_news = Table('vip_news', meta, autoload=True, autoload_with=engine)
                ins = vip_news.insert()
                connection.execute(ins, v_name=v_name, posted_time=TmStamp, title=TTitle, URL=HUrl, text=TText,
                                   fwd_fre=Tretweet, likes=Tlikes)

            except:
                # print("sql error")
                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]
                Tretweet = re_tweet[i]
                Tlikes = like[i]

                TTitle = fix(TTitle)
                TText = fix_text1(TText)
                # add quotation to text start and end
                TText = "'''" + TText + "'''"

                # get Table object and insert data
                meta = MetaData()
                engine = get_db()[2]
                connection = get_db()[1]
                vip_news = Table('vip_news', meta, autoload=True, autoload_with=engine)
                ins = vip_news.insert()
                try:
                    connection.execute(ins, v_name=v_name, posted_time=TmStamp, title=TTitle, URL=HUrl, text=TText,
                                       fwd_fre=Tretweet, likes=Tlikes)
                except:
                    connection.execute(ins, v_name=v_name, posted_time=TmStamp, title=TTitle, URL=HUrl, text="N/A",
                                       fwd_fre=Tretweet, likes=Tlikes)

    @classmethod
    def set_simifre(cls, temp, H_url, title, news_text, frequency, search_job_id):

        # store timestamp, url, title, text, similarity frequency into table 'newsinfo_simifre' in database 'twitternews'
        # use re.compile to remove all except things kept in []
        for i in range(len(temp)):
            try:
                TmStamp = ''.join(temp[i][0])
                HUrl = ''.join(H_url[i][0])
                TTitle = title[i]
                try:
                    if len(''.join(news_text[i][0])) == 0:
                        TText = 'No Text Available in this tweet'
                    else:
                        TText = ''.join(news_text[i][0])
                except:
                    TText = 'No URL Available in this tweet'
                fre = str(frequency[i][0])

                TTitle = fix(TTitle)
                TText = fix(TText)

                # get Table object and insert data
                meta = MetaData()
                engine = get_db()[2]
                connection = get_db()[1]
                newinfo_simifre = Table('newinfo_simifre', meta, autoload=True, autoload_with=engine)
                ins = newinfo_simifre.insert()
                connection.execute(ins, posted_time=TmStamp, title=TTitle, URL=HUrl, search_job_id=str(
                    search_job_id), text=TText, similatiry_fre=fre)


            except:
                print("sql error")
                TmStamp = ''.join(temp[i][0])
                HUrl = ''.join(H_url[i][0])
                TTitle = title[i]
                if len(''.join(news_text[i][0])) == 0:
                    TText = 'No Text Available in this link'
                else:
                    TText = ''.join(news_text[i][0])
                fre = str(frequency[i][0])

                TTitle = fix(TTitle)
                TText = fix(TText)
                # add quotation to text start and end
                TText = "'''" + TText + "'''"

                # get Table object and insert data
                meta = MetaData()
                engine = get_db()[2]
                connection = get_db()[1]
                newinfo_simifre = Table('newinfo_simifre', meta, autoload=True, autoload_with=engine)
                ins = newinfo_simifre.insert()
                connection.execute(ins, posted_time=TmStamp, title=TTitle, URL=HUrl, search_job_id=str(
                    search_job_id), text=TText, similatiry_fre=fre)


def fix(text):
    regex = re.compile('[^a-zA-Z0-9\,\.\s]')
    fixed_text = regex.sub('', text)
    return fixed_text


def fix_text1(text):
    if isinstance(text, str):
        text = fix(text)
    else:
        text = ""
    return text


def get_db():
    engine = create_engine('mysql+pymysql://' + user + ':' + password + '@' + host + ':3306/' + database, echo=False)
    connection = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, connection, engine


def get_similarity_result(search_job):
    # print(search_job.id, search_job.keyword)
    session = get_db()[0]
    connection = get_db()[1]
    newingSiffreList = session.query(NewinfoSimifre).filter(NewinfoSimifre.search_job_id == search_job.id).order_by(
        desc(NewinfoSimifre.similatiry_fre)).limit(20)
    connection.close()
    return newingSiffreList


def create_search_job(search_job):
    session = get_db()[0]
    connection = get_db()[1]
    result = get_search_job_in_db(search_job, session)
    if (result != None):
        print("***this search job already existed in search_job table!***")
    else:
        session.add(search_job)
        session.commit()
        result = get_search_job_in_db(search_job, session)
        search_task(str(search_job.keyword), int(search_job.month), int(search_job.start_date),
                    int(search_job.end_date), int(search_job.limit), int(result.id))
        # search_task("bitcoin", 10, 1, 4, 4, 72)
    connection.close()
    return result


def get_search_job_in_db(search_job, session):
    result = session.query(SearchJob).filter(SearchJob.keyword == search_job.keyword) \
        .filter(SearchJob.limit == search_job.limit) \
        .filter(SearchJob.start_date == search_job.start_date) \
        .filter(SearchJob.month == search_job.month) \
        .filter(SearchJob.end_date == search_job.end_date).first()
    return result


def get_vip_in_db(v_name, limit):
    engine = get_db()[2]
    meta = MetaData()
    meta.reflect(bind=engine) # Automatically creates Table entries in this MetaData for any table available in the database but not yet present in the MetaData
    table_list = []
    for table in reversed(meta.sorted_tables):
        table_list.append(str(table))
    if 'vip_news' in table_list:
        print('table ' + str(table) + ' already exits in database\n')
        vip_search_task(v_name, limit)
    else:
        print('table vip_news' + ' is being built in database\n')
        Base.metadata.create_all(engine)
        print("vip_search_task starts\n")
        vip_search_task(v_name, limit)
    return engine, VIPNews


def search_task(keyword, month, start_day, end_day, limit, search_job_id):
    tim = []
    short_url = []
    docker = []  # docker to store results of query_tweets for one search
    title = []
    if start_day != 0 and end_day != 0 and start_day < end_day:
        # for i in range(x, y):
        for tweet in query_tweets(
                        keyword + "%20since%3A2017-{}-{}%20until%3A2017-{}-{}".format(month, start_day, month, end_day),
                limit)[:limit]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')
            text = text.replace('\n', '')
            text = re.sub(r'http\S+.*[\r\n]*', '', text, flags=re.MULTILINE)
            title.append(text)
            tim.append(tweet.timestamp)
            if start_day == end_day: break
    else:
        for tweet in query_tweets(keyword, limit)[:limit]:
            short_url.append(tweet.url)
            docker.append(tweet)
            text = tweet.text.encode('utf-8').decode('utf-8')  # decode() removes binary mark: b'
            text = text.replace('\n', '')
            text = re.sub(r'http\S+.*[\r\n]*', '', text, flags=re.MULTILINE)
            title.append(text)
            tim.append(tweet.timestamp)
            # if x == y: break
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
        print(str((news_title + 1)) + " news titles have been scraped")
        print("News Title: " + title[news_title])
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
        Database.set_raw_all(temp, H_url, title, news_text, search_job_id)
        print("raw data write into database complete\n")

        # write raw data to database newinfo_simifre
        TitleFrequency = Similarity.get_simi_titlefre(
            title)  # invoke function in similarity class to get title-frequency after similariy screen

        frequency_similarity = list(TitleFrequency.values())  # dict to list
        title_similarity = list(TitleFrequency.keys())  # dict to list
        Frequency_similarity = TitleFrequency.values()
        Title_similarity = TitleFrequency.keys()
        URL_similarity = [dict_tu[titl] for titl in Title_similarity]
        TmStamp_similarity = [dict_tt[titl] for titl in Title_similarity]
        Text_similarity = [dict_tx[titl] for titl in Title_similarity]

        Database.set_simifre(TmStamp_similarity, URL_similarity, title_similarity, Text_similarity,
                             frequency_similarity, search_job_id)
        print("similarity screened data write into database complete\n")

        return


def vip_search_task(V_name, l):
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
        Database.set_raw_vip(V_name, temp, H_url, title, news_text, re_tweet, like)

        print("raw data write into database complete\n")

    return
