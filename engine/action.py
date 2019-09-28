from typing import Dict
from .event import Event


class Action:
    def __init__(self):
        self._send_event = lambda event: None
        self._send_message = lambda message, user_id: None

    def set_send_event(self, send_event):
        self._send_event = send_event

    def set_send_message(self, send_message):
        self._send_message = send_message

    def event(self, event_text, user_id, message):
        self._send_event(Event(event_text, user_id, message))

    def run(self, message: str, user_id: str, context: Dict):
        print("Base action is not redefined")

    def go_run(self, message: str, user_id: str, context: Dict):
        result = self.run(message, user_id, context)
        self._send_message(result, user_id)
