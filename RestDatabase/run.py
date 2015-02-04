#from app import app, db, models, controllers
#from app import app,db
import sys
from app import app

print "app: ", dir(app)

# > python run.py
if len(sys.argv) == 1:
    app.run(host='127.0.0.1', debug=True)

# > python run.py setup


'''
elif sys.argv[1] == 'setup':
    db.drop_all()
    db.create_all()
'''
