class Skill:
    def __init__(self, name):
        self.name = name

    def run(self):
        pass


class Dispatcher:
    def __init__(self):
        self.skills = {}

    def add_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    def classify(message):
        pass

    def start(self):
        pass


if __name__ == "__main__":
    disp = Dispatcher()
    disp.start()
