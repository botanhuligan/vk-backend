from typing import Dict
from datetime import datetime
from engine import Skill, Action

simple_skill = Skill("static/skill.yaml")


# -------- Custom Actions --------
class SayHelloAction(Action):
    def run(self, message, user_id, context: Dict):
        print("CURRENT_CONTEXT: " + str(context))
        context["action"] = "SayHelloAction"
        return "Здравствуйте, {0}! Вы хотите узнать сколько времени?".format(user_id)


class GetTimeAction(Action):
    def run(self, message, user_id, context: Dict):
        print("CURRENT_CONTEXT: " + str(context))
        context["action"] = "GetTimeAction"
        self.event("RESTART", user_id)
        return "Сейчас {0}".format(datetime.now())


class GoodByeAction(Action):
    def run(self, message, user_id, context: Dict):
        context["action"] = "GoodByeAction"
        print("CURRENT_CONTEXT: " + str(context))
        self.event("RESTART", user_id)
        return "Нет так нет. До скорого свидания, {0}!".format(user_id)


# -------- Register Actions --------
simple_skill.register_action("say_hello_action", SayHelloAction)
simple_skill.register_action("get_time_action", GetTimeAction)
simple_skill.register_action("good_bye_action", GoodByeAction)
