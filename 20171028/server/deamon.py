import json

from flask import Flask, request, Response
from flask_cors import CORS

from server.database import get_similarity_result, SearchJob, create_search_job

app = Flask(__name__)
CORS(app)


@app.route("/search_job", methods=['GET'])
def get_search():

    keyword = request.args.get('keyword')
    month = request.args.get('month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit')
    print("your search job is:")
    print("search keyword:" + str(keyword))
    print("month:"+str(month))
    print("end_date:"+str(end_date))
    print("start_date:"+str(start_date))
    print("search result limit:"+ str(limit))

    search_job = SearchJob(keyword=keyword, month=month,start_date=start_date,end_date=end_date,limit=limit)
    search_job = create_search_job(search_job)
    newing_siffre_list = list(get_similarity_result(search_job))
    jsonStr = json.dumps([e.toJSON() for e in newing_siffre_list])
    return Response(jsonStr, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
