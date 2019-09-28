from datetime import datetime
from typing import Dict
from engine import Skill, Action, Answer

legend_skill = Skill("static/legend_skill.yaml")


# -------- Custom Actions --------
class SayTimeAction(Action):
    def run(self, message, user_id, context: Dict):
        return Answer("Сейчас {0}".format(datetime.now().strftime("%H:%M")))


# -------- Register Actions --------
legend_skill.register_action("say_time", SayTimeAction)
