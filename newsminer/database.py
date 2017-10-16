import pymysql
import re
from similarity import Similarity


class Database:
    @classmethod
    def clear_table(self):
        print("start to clear all information in tables\n")
        conn = pymysql.connect(host="127.0.0.1", user="root", passwd="root", db="twitternews")
        sql1 = "delete from newinfo_raw"
        sql2 = "delete from newinfo_simifre"
        conn.query(sql1)
        conn.query(sql2)
        print("table clear completes\n")

    @classmethod
    def set_raw(cls, temp, H_url, title, news_text):


        ################################ database for raw starts #############################################


        # store timestamp, url, title, text into table 'newsinfo' in database 'twitternews'
        conn = pymysql.connect(host = "127.0.0.1", user = "root", passwd = "root", db = "twitternews")

        # use re.compile to remove all except things kept in []
        for i in range(len(temp)):
            try:

                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]


                regex = re.compile('[^a-zA-Z0-9\,\.\s]')
                TTitle = regex.sub('', TTitle)
                if isinstance(TText, str):
                    TText = regex.sub('', TText)
                else:
                    TText = ""
                sql = "insert into newinfo_raw(Tstamp, Title, URL, Texts) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "')"
                conn.query(sql)

            except:
                print("sql error")

                TmStamp = temp[i]
                HUrl = H_url[i]
                TTitle = title[i]
                TText = news_text[i]


                regex = re.compile('[^a-zA-Z0-9\,\.\s]')
                TTitle = regex.sub('', TTitle)
                if isinstance(TText, str):
                    TText = regex.sub('', TText)
                else:
                    TText = ""
                # add quotation to text start and end
                TText = "'''" + TText + "'''"

                # insert into database after adding new quotation
                sql = "insert into newinfo_raw(Tstamp, Title, URL, Texts) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "')"
                conn.query(sql)

        conn.close()

################################# database for raw ends ##################################################



################################# database for similarity frequency starts ################################################

    @classmethod
    def set_simifre(cls, temp, H_url, title, news_text, frequency):

        # store timestamp, url, title, text, similarity frequency into table 'newsinfo_simifre' in database 'twitternews'
        conn = pymysql.connect(host = "127.0.0.1", user = "root", passwd = "root", db = "twitternews")

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
                        TText =''.join(news_text[i][0])
                except:
                    TText = 'No URL Available in this tweet'
                fre = str(frequency[i][0])

                regex = re.compile('[^a-zA-Z0-9\,\.\s]')
                TTitle = regex.sub('', TTitle)
                TText = regex.sub('', TText)

                sql = "insert into newinfo_simifre(Tstamp, Title, URL, Text, Similatiry_Fre) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "','" + fre + "')"
                conn.query(sql)

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

                regex = re.compile('[^a-zA-Z0-9\,\.\s]')
                TTitle = regex.sub('', TTitle)
                TText = regex.sub('', TText)
                # add quotation to text start and end
                TText = "'''" + TText + "'''"



                # insert into database after adding new quotation
                sql = "insert into newinfo_simifre(Tstamp, Title, URL, Text, Similatiry_Fre) values('" + TmStamp + "','" + TTitle + "','" + HUrl + "','" + TText + "','" + fre + "')"
                conn.query(sql)

                '''
                print("*********************************************")
                print(TmStamp)
                print(HUrl)
                print(TTitle)
                print(news_text)
                print(TText)
                print("*********************************************")
                '''
        conn.close()

        ################################# database for frequency ends ################################################

