from .message import Message
from .user import User
from .skill import Skill
from .utils import *


class Dispatcher:
    def __init__(self):
        self.skills = {}
        self._users = {}
        self._events = {}

    def add_skill(self, filename):
        skill = Skill(filename)
        self.skills[skill.name] = skill
        log.info("Skill <{0}> added".format(skill.name))

    def build_events(self, filename):
        data = read_yaml(filename)
        for event in data:
            log.info("Event <{0}> added;".format(event))
            for phrase in data[event]:
                if event in self._events:
                    self._events[event].append(phrase.lower())
                    continue
                self._events[event] = [phrase.lower()]

    def event_classify(self, message_text, history_message_texts):
        """
        TODO: request with message_text, history_message_texts return current event
        :param message:
        :param user:
        :return:
        """

        for event, phrases in self._events.items():
            if message_text.lower() in phrases:
                return event
        return None

    def start(self):
        pass

    def _new_user(self, user_id) -> User:
        self._users[user_id] = User(user_id)
        return self._users[user_id]

    def _get_user(self, user_id) -> User:
        if user_id in self._users:
            return self._users[user_id]
        return self._new_user(user_id)

    def _unknown_event(self, event):
        log.warning(UNKNOWN_EVENT.format(event))

    def run(self, message: Message):
        if not message.user_id:
            raise Exception(USER_NOT_DEFINED)
        user = self._get_user(message.user_id)
        event = self.event_classify(message.message_text, user.history)

        for skill_id, state in user.get_skill():
            if self.skills[skill_id].can_handle(event, state):
                self.skills[skill_id].run(user, event, state)
                return

        for skill_id, skill in self.skills.items():
            if skill_id not in user.skill_stack and skill.can_handle(event):
                self.skills[skill_id].run(user, event)
                return

        self._unknown_event(event)
