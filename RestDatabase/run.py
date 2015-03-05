#from app import app, db, models, controllers
#from app import app,db
import sys
from app import socketio, app

# > python run.py
if len(sys.argv) == 1:
    socketio.run(app,host="0.0.0.0", port=5000)
    
elif sys.argv[1] == "debug":
    socketio.run(app,host="127.0.0.1", port=5000, use_reloader=False)

# > python run.py setup
elif sys.argv[1] == "setup":
    from app import db
    db.drop_all()
    db.create_all()

    from app.models import *
    running = Activity("running")
    running_q1 = Question(running, "How much time do you want to spend running?")
    running_q2 = Question(running, "How far do you want to run?")
    running.questions.append(running_q1)
    running.questions.append(running_q2)
    db.session.add(running)
    db.session.commit()
    print "Setup complete."
