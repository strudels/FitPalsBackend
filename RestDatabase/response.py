class Response():
    def __init__(self, status=200, message="", value=None):
        self.status = status
        self.message = message
        self.value = value
