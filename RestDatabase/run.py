#from app import app, db, models, controllers
#from app import app,db
import sys
from app import app

# > python run.py
if len(sys.argv) == 1:
    app.run(host="127.0.0.1")
    
elif sys.argv[1] == "debug":
    app.run(host="127.0.0.1", debug=True, use_reloader=False)

# > python run.py setup
elif sys.argv[1] == "setup":
    from app import db
    db.drop_all()
    db.create_all()

elif sys.argv[1] == "test":
    app.run(host="127.0.0.1", debug=True)
    from app.tests import *
    unittest.main()
    sys.exit()
