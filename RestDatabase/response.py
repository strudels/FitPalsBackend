import simplejson as json
class Response():
    def __init__(self, success=True, error_msg="", value=None):
        self.success = success
        self.error_msg = error_msg
        self.value = value

    def to_json(self):
        return json.dumps({
            "success": self.success,
            "error_msg": self.error_msg,
            "value": self.value
        })
