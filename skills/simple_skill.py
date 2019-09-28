from typing import Dict
from datetime import datetime
from engine import Skill, Action, Answer

simple_skill = Skill("static/skill.yaml")


# -------- Custom Actions --------
class SayHelloAction(Action):
    def run(self, message, user_id, context: Dict):
        context["name"] = user_id
        return Answer(
            "Здравствуйте, {0}! Вы хотите узнать сколько времени?".format(user_id)
        )


class GetTimeAction(Action):
    def run(self, message, user_id, context: Dict):
        return Answer("Сейчас {0}".format(datetime.now()))


# -------- Register Actions --------
simple_skill.register_action("say_hello_action", SayHelloAction)
simple_skill.register_action("get_time_action", GetTimeAction)
