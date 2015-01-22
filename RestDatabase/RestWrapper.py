import Service

from flask import Flask
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
    if not request.form['user_info']: return "No Data given to update"
    if not request.form['user_id']:
        return json.dumps(Service.update_user(request.form['user_info'],db))
    return json.dumps(Service.update_user(request.form['user_info'],db,
        request.form['user_id']))

if __name__=='__main__':
    app.run(host='0.0.0.0')
