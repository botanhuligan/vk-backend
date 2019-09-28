class Answer:
    def __init__(self, message_text, message_say=None, url_img=None, url_voice=None):
        self.message_text = message_text
        self.message_say = message_say if message_say else message_text
        self.url_img = url_img
        self.url_voice = url_voice
        self.user_id = None

    def set_user(self, user_id):
        self.user_id = user_id

    def json(self):
        result = {}
        if self.message_text:
            result["message_text"] = self.message_text
        if self.message_say:
            result["message_say"] = self.message_say
        if self.url_img:
            result["url_img"] = self.url_img
        if self.url_voice:
            result["url_voice"] = self.url_voice
        if self.user_id:
            result["user_id"] = self.user_id
        return result
