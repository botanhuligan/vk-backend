from .message import Message
from .user import User
from log import log
from .utils import read_yaml

NO_NAME_IN_SKILL_YAML = "No name in skill from file {0}"
NO_DEFAULT_STATE = "No default name in skill from file {0}"
USER_NOT_DEFINED = "User is not defined in message"
UNKNOWN_EVENT = "Unknown event: {0}"
INCORRECT_STATE = "Wrong state: {0}"


class State:
    def __init__(self, name):
        self.name = name
        self.action = None
        self.edges = {} # event:state

    def set_action(self, action):
        self.action = action

    def add_edge(self, event, state):
        self.edges[event] = state

    def has_event(self, event):
        return any([event == key for key in self.edges])

    def next_state(self, event):
        if event in self.edges:
            return self.edges[event]
        else:
            return None


class Skill:
    def __init__(self, filename):
        self.name = None
        self.default_state = None
        self.states = {}
        self.build(filename)

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

    def run(self, user: User, event: str, state: str or None = None) -> None:
        """
        if state == None -> init state

        :param user:
        :param event:
        :param state:
        :return:
        """
        if not state:
            state = self.default_state
        next_state = self.states[state].next_state(event)

        if not next_state:
            log.error("No next state in skill={0} state={1}".format(self.name, state))
            return

        log.debug("RUN_ACTION: " + self.states[next_state].action)
        user.update_skill(self.name, next_state)

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
