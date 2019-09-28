from datetime import datetime


class SkillStackObj:
    def __init__(self, state):
        self.time = datetime.now()
        self.state = state

    def update(self, state):
        self.time = datetime.now()
        self.state = state


class User:
    def __init__(self, name):
        self.name = name
        self.history = []
        self.skill_stack = {}  # skill_id : SkillStackObj
        self.context = {}

    def update_skill(self, skill_id, state):
        if skill_id not in self.skill_stack:
            self.skill_stack[skill_id] = SkillStackObj(state)
            return

        self.skill_stack[skill_id].update(state)

    def get_skill(self):
        for skill in sorted(self.skill_stack.items(), key=lambda kv: kv[1].time, reverse=True):
            yield skill[0], skill[1].state

    def add_history(self, message):
        self.history.append(message)

    def get_history(self, amount):
        return self.history[-amount:][::-1]


if __name__ == "__main__":
    user = User("Test user")
    user.update_skill("1", "1")
    user.update_skill("2", "10")
    user.update_skill("4", "4")
    user.update_skill("3", "3")
    user.update_skill("2", "2")

    for a in user.get_skill():
        print(a)
