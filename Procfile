web: gunicorn --pythonpath=RestDatabase --worker-class geventworker.StopCrashingInGunicornWorker app:app
setup: python RestDatabase/run.py setup
