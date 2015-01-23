import Service

from flask import Flask
from flask import request
import simplejson as json

app=Flask(__name__)
db = Service.get_matchmaker_db()

@app.route('/')
def hello_world():
    return 'Hello World!'

#Insert or Update a user in the matchmaking system
@app.route('/update-user', methods=['POST'])
def update_user():
    global db
    if not "user_info" in request.form.keys(): return "No Data given to update"
    if not "user_id" in request.form.keys():
        return Service.update_user(json.loads(request.form['user_info']),db)
    return Service.update_user(json.loads(request.form['user_info']),
        db, request.form['user_id'])

@app.route('/search',methods=['GET'])
def user_search():
    global db
    required_params = ["user_id","radius"]
    if len(set(required_params).intersection(request.args.keys())) != 2:
        return "Missing Parameters"
    return json.dumps(Service.get_nearby_users(request.args.get("user_id",''),
        int(request.args.get('radius','')),db))

@app.route('/users',methods=['GET'])
def get_user_data():
    global db
    if not "user_id" in request.args.keys(): return "No User Id Specified"
    return json.dumps(Service.get_user_data(request.args["user_id"],
        request.args.getlist('attributes'), db))


if __name__=='__main__':
    app.run(host='0.0.0.0')
