from typing import Dict, Type

from .answer import Answer
from .event import Event
from .action import Action
from .user import User
from .state import State
from .utils import *
import re

class Skill:
    def __init__(self, filename):
        self.name = None
        self.default_state = None
        self.states = {}
        self.build(filename)
        self.actions = {}
        self._send_log = lambda mess, user_id: None
        self._send_message = lambda mess, user_id: None
        self._send_event = lambda event: None

    def set_send_event(self, send_event):
        self._send_event = send_event

        for action in self.actions.values():
            action.set_send_event(send_event)

    def set_send_log(self, _send_log):
        self._send_log = _send_log

    def set_send_message(self, send_message):
        self._send_message = send_message

        for action in self.actions.values():
            action.set_send_message(send_message)

    def build(self, filename):
        data = read_yaml(filename)
        if data:
            if "name" not in data:
                raise Exception(NO_NAME_IN_SKILL_YAML)

            self.name = data["name"]
            if "states" in data:
                for state_id in data["states"]:
                    state = State(state_id)
                    state_data = data["states"][state_id]

                    if "edges" not in state_data:
                        continue

                    edges = state_data["edges"]
                    for event, next_state in edges.items():
                        state.add_edge(event, next_state)

                    if "action" in state_data:
                        state.set_action(state_data["action"])

                    if "event" in state_data:
                        state.set_event(state_data["event"])

                    if "answer" in state_data:
                        state.set_answer(state_data["answer"])

                    if "is_default" in state_data:
                        self.default_state = state_id

                    self.states[state_id] = state

        # Проверка корректности
        for state_id, state in self.states.items():
            for event, next_state in state.edges.items():
                if next_state not in self.states:
                    raise Exception(INCORRECT_STATE.format(next_state))

        if not self.default_state:
            raise Exception(NO_DEFAULT_STATE.format(filename))

    def change_state(self, user, state, next_state):
        user.update_skill(self.name, next_state)
        self._send_log("CHANGE_STATE: " + state + "--->" + next_state, user.name)

    @staticmethod
    def _get_entities(text):
        return re.findall(r"\{([^\}]*)\}", text)

    def answer_to_user(self, user, answer):
        for entity in self._get_entities(answer):
            if entity not in user.context:
                answer = answer.replace("{%s}" % entity, "")
            else:
                answer = answer.replace("{%s}" % entity, user.context[entity])

        self._send_message(Answer(answer), user.name)

    def run(self, user: User,
            event: str,
            state: str or None = None,
            message: str or None = None) -> None:
        """
        if state == None -> init state

        :param user:
        :param event:
        :param state:
        :param message:
        :return:
        """
        if not state:
            state = self.default_state
        next_state = self.states[state].next_state(event)

        if not next_state:
            log.error("No next state in skill={0} state={1}".format(self.name, state))
            return

        if self.states[next_state].action:
            try:
                self.run_action(
                    self.states[next_state].action,
                    str(message),
                    user.name,
                    user.context
                )
            except Exception as exception:
                log.error(exception)
                if self.states[next_state].answer:
                    self.answer_to_user(user, self.states[next_state].answer)

        elif self.states[next_state].answer:
            self.answer_to_user(user, self.states[next_state].answer)

        if self.states[next_state].event:
            self._send_event(Event(self.states[next_state].event, user.name, message))
        if message:
            user.add_history(message)

        self.change_state(user, state, next_state)

    def can_handle(self, event, state=None) -> bool:
        """
        Returns True if can else False

        :param event:
        :param state:
        :return:
        """
        if not state:
            state = self.default_state
        if state not in self.states:
            return False
        return self.states[state].has_event(event)

    def register_action(self, action_id: str, action: Type[Action]):
        self.actions[action_id] = action()

    def run_action(self, action_id: str, message: str, user_id: str, context: Dict):
        if action_id in self.actions:
            self.actions[action_id].go_run(message, user_id, context)
        else:
            log.error("No such action: {0}".format(action_id))
