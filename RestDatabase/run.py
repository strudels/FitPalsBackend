#from app import app, db, models, controllers
#from app import app,db
import sys
import signal
from app import socketio, app
from app.utils import AsyncNotifications

def sigint_handler(signal, frame):
    #kill thread responsible for cleaning up async call threads
    AsyncNotifications.manager_thread._Thread__stop()
    sys.exit()
signal.signal(signal.SIGINT, sigint_handler)

# > python run.py
if len(sys.argv) == 1:
    socketio.run(app,host="0.0.0.0", port=5000)
    
elif sys.argv[1] == "debug":
    socketio.run(app,host="127.0.0.1", port=5000, use_reloader=False)

# > python run.py setup
elif sys.argv[1] == "setup":
    from app import reset_app
    reset_app()
    print "Setup complete."
    AsyncNotifications.manager_thread._Thread__stop()
    
    
