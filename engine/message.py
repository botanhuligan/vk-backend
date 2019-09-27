class Message:
    def __init__(self, message):
        self.message_text = message["message_text"] if "message_text" in message else None
        self.user_id = message["user_id"] if "user_id" in message else None
