import json
from flask import Flask, request, Response
from flask_cors import CORS
from model.aggregator_model import get_similarity_result, SearchJob, create_search_job, get_vip_in_db, Database
from sqlalchemy.orm import sessionmaker
from model.query import set_init_url

app = Flask(__name__)
CORS(app)


@app.route("/search_job_all", methods=['GET'])
def get_search1():
    # set init_url
    search_url = "https://twitter.com/search?l=en&f=tweets&vertical=default&q={q}"
    set_init_url(search_url)

    keyword = request.args.get('keyword')
    month = request.args.get('month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit')
    print("your search job is:")
    print("search keyword:" + str(keyword))
    print("month:" + str(month))
    print("end_date:" + str(end_date))
    print("start_date:" + str(start_date))
    print("search result limit:" + str(limit))

    choice1 = input("do you want to clear database tables?(y/n)")
    if choice1 == "y":
        Database.clear_table("newinfo_raw")
        Database.clear_table("newinfo_simifre")

    choice2 = input("do you want to clear search_job tables?(y/n)")
    if choice2 == "y":
        Database.clear_table("search_job")

    search_job = SearchJob(keyword=keyword, month=month, start_date=start_date, end_date=end_date, limit=limit)
    search_job = create_search_job(search_job)
    newing_siffre_list = list(get_similarity_result(search_job))
    jsonStr = json.dumps([e.toJSON() for e in newing_siffre_list])
    return Response(jsonStr, mimetype='application/json')


@app.route("/search_job_vip", methods=['GET'])
def get_search2():

    search_url = "https://twitter.com/{q}?lang=en"
    set_init_url(search_url)

    v_name = request.args.get('v_name')
    limit = int(request.args.get('limit'))
    print("your search job is:")
    print("search keyword:" + str(v_name))
    print("search result limit:" + str(limit))
    engine, VIPNews = get_vip_in_db(v_name, limit)

    # query data from database
    Session = sessionmaker(bind=engine)
    session = Session()
    db_table_query = session.query(VIPNews).limit(20)
    result = list(db_table_query)
    jsonStr = json.dumps([e.toJSON() for e in result])
    return Response(jsonStr, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
