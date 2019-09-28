from typing import Dict
from multiprocessing import Queue
import re

from .answer import Answer
from .action import Action
from .message import Message
from .user import User
from .skill import Skill
from .utils import *
from .event import Event


class Dispatcher:
    def __init__(self):
        self.skills = {}
        self._users = {}
        self._events = {}
        self.queue = Queue()
        self.is_alive = True
        self._send_message = lambda message: None
        self._send_log = lambda message: None

    def kill(self):
        self.is_alive = False

    def add_skill(self, skill):
        if not skill.name:
            raise Exception("No skill name")

        self.skills[skill.name] = skill

    # Вопрос: как более очевидно: руками создавать скилл или автоматически?
    # def add_skill(self, filename, actions: Dict[str, Action]):
    #
    #     skill = Skill(filename)
    #     for action_id, action in actions.items():
    #         skill.register_action(action_id, action)
    #
    #     self.skills[skill.name] = skill
    #     log.info("Skill <{0}> added".format(skill.name))

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
        reg = re.compile('[^a-zA-Zа-яА-Я ]')
        message_text = reg.sub('', message_text)
        print(message_text)
        for event, phrases in self._events.items():
            if message_text.lower() in phrases:
                return event
        return None

    def set_send_message(self, send_message):
        self._send_message = send_message

    def send_message(self, message, user_id):
        message.set_user(user_id)
        log.debug("SEND_MESSAGE" + str(message.message_text))
        log.debug("SEND_MESSAGE" + str(message.message_text))
        self._send_message(message.json())

    def set_send_log(self, send_message):
        self._send_log = send_message

    def send_log(self, message, user_id):
        mess = {"log": message, "user_id": user_id}
        self._send_log(mess)

    def start(self):
        for skill in self.skills.values():
            skill.set_send_event(self.add_event)
            skill.set_send_message(self.send_message)
            skill.set_send_log(self.send_log)

        log.info("Dispatcher started")
        while self.is_alive:
            event = self.queue.get()
            self.run(event)

    def _new_user(self, user_id) -> User:
        self._users[user_id] = User(user_id)
        return self._users[user_id]

    def _get_user(self, user_id) -> User:
        if user_id in self._users:
            return self._users[user_id]
        return self._new_user(user_id)

    def _unknown_event(self, event, user_id):
        log.warning(UNKNOWN_EVENT.format(event))
        self.send_message(Answer("К сожалению, пока я тебя не понимаю..."), user_id)

    def message_handler(self, message: Message):
        # if message.message_text == "EXIT":
        #     self.is_alive = False
        #     self.queue.put(Event("EXIT", None))
        #     return

        if not message.user_id:
            raise Exception(USER_NOT_DEFINED)
        user = self._get_user(message.user_id)
        event_text = self.event_classify(message.message_text, user.history)
        self.add_event(Event(event_text, user.name, message.message_text))

    def add_event(self, event):
        self.queue.put(event)

    def run(self, event: Event):
        self.send_log("Event: {0}".format(event.event), event.user_id)

        user = self._get_user(event.user_id)
        for skill_id, state in user.get_skill():
            if self.skills[skill_id].can_handle(event.event, state):
                self.skills[skill_id].run(user, event.event, state, event.message)
                return

        for skill_id, skill in self.skills.items():
            if skill_id not in user.skill_stack and skill.can_handle(event.event):
                self.skills[skill_id].run(user, event.event, message=event.message)
                return

        self._unknown_event(event.event, user.name)
