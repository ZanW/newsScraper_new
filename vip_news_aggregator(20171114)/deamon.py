import json
from datetime import datetime
from flask import Flask, request, Response
from flask_cors import CORS
import MySQLdb
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import search_task

app = Flask(__name__)
CORS(app)

host = "127.0.0.1"
password = "root"
user = "root"
database = "news"

Base = declarative_base()

class VIPNews(Base):
    __tablename__ = 'vip_news'
    id = Column(Integer, primary_key=True)
    v_name = Column(String(255), nullable=True)
    posted_time = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    URL = Column(String(255), nullable=True)
    text = Column(Text, nullable=True)
    fwd_fre = Column(Integer, nullable=True)
    likes = Column(Integer, nullable = True)

    def toJSON(self):
        return {'VIP_Name': self.v_name,
                'Posted_Time': self.posted_time,
                'Title': self.title,
                'URL': self.URL,
                'Fwd_Fre': self.fwd_fre,
                'Likes': self.likes,
                }


@app.route("/search_job", methods=['GET'])
# We then use the route() decorator to tell Flask what URL should trigger our function.
# The function is given a name which is also used to generate URLs for that particular
# function, and returns the message we want to display in the user’s browser.
def get_search():
    v_name = request.args.get('v_name')
    limit = int(request.args.get('limit'))
    print("your search job is:")
    print("search keyword:" + str(v_name))
    print("search result limit:"+ str(limit))

    engine = create_engine('mysql+pymysql://' + user + ':' + password + '@' + host + ':3306/' + database,
                           echo=False)
    connection = engine.connect()

    db = MySQLdb.connect(host = host, user = user, passwd=password, db=database)
    cursor = db.cursor()
    stmt = "SHOW TABLES LIKE 'vip_news'"
    cursor.execute(stmt)
    result = cursor.fetchone()
    if result:
        connection.close()
        print('table ' + result[0] + ' already exits in database')
        search_task(v_name, limit)
    else:
        print('table vip_news' + ' is being built in database')
        Base.metadata.create_all(engine)
        connection.close()
        print("search_task starts")
        search_task(v_name, limit)

    # query data from database
    Session = sessionmaker(bind=engine)
    session = Session()
    db_table_query = session.query(VIPNews).limit(20)
    result = list(db_table_query)
    jsonStr = json.dumps([e.toJSON() for e in result])
    return Response(jsonStr, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
