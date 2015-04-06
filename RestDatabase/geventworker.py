from socketio.sgunicorn import GeventSocketIOWorker

class StopCrashingInGunicornWorker(GeventSocketIOWorker):
    policy_server = False
