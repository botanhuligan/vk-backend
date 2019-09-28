from typing import Dict
from engine import Skill, Action

where_is_skill = Skill("static/where_is_skill.yaml")


# -------- Custom Actions --------
class WhereIsAction(Action):
    def run(self, message, user_id, context: Dict):
        if "entity" not in context:
            return "К сожалению, я не знаю, где это находится."
        else:
            entity = context["entity"]
            if entity["type"] == "toilet":
                return "тут будет ответ, как искать туалет"
            elif entity["type"] == "author":
                return "тут будет ответ, как искать автора"
        return "Я Вас не совсем понял, уточните, пожалуйста, свой запрос."


# -------- Register Actions --------
where_is_skill.register_action("where_is_action", WhereIsAction)
