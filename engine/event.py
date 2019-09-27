
class Event:
    def __init__(self, event, user_id, message=None):
        self.event = event
        self.message = message
        self.user_id = user_id
