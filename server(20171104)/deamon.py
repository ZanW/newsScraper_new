import json
from datetime import datetime

from flask import Flask, request, Response
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from database import search_task

app = Flask(__name__)
CORS(app)

host = "127.0.0.1"
password = "root"
user = "root"
database = "news"

Base = declarative_base()

class VIPNews(Base):
    __tablename__ = 'VIPNews'
    id = Column(Integer, primary_key=True)
    VName = Column(String(255), nullable=True)
    Time = Column(String(255), nullable=True)
    Title = Column(String(255), nullable=True)
    URL = Column(String(255), nullable=True)
    Text = Column(Text, nullable=True)
    Fwd_fre = Column(Integer, nullable=True)

@app.route("/search_job", methods=['GET'])
# We then use the route() decorator to tell Flask what URL should trigger our function.
# The function is given a name which is also used to generate URLs for that particular
# function, and returns the message we want to display in the user’s browser.
def get_search():
    V_name = request.args.get('V_name')
    limit = int(request.args.get('limit'))
    print("your search job is:")
    print("search keyword:" + str(V_name))

    print("search result limit:"+ str(limit))
    engine = create_engine('mysql+pymysql://' + user + ':' + password + '@' + host + ':3306/' + database,
                           echo=False)
    connection = engine.connect()
    Base.metadata.create_all(engine)
    connection.close()
    search_task(V_name, limit)

    newing_siffre_list = datetime.now()
    try:
        jsonStr = json.dumps([e.toJSON() for e in newing_siffre_list])
        return Response(jsonStr, mimetype='application/json')
    except:
        return Response(('Only English language is supported. '
                         '%s is not valid input.' % "hao dad adfa"),
                         content_type='text/plain; charset=utf-8')



'''
    # newing_siffre_list = list(get_similarity_result(search_job))
    # jsonStr = json.dumps([e.toJSON() for e in newing_siffre_list])
    # return Response(jsonStr, mimetype='application/json')
    VIPNews_list = list(job)
    jsonStr = json.dumps([e.toJSON() for e in VIPNews_list])
    return Response(jsonStr, mimetype='application/json')
'''
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
