from typing import Dict

import requests

from engine import Skill, Action, Answer

where_is_skill = Skill("static/tell_about_img.yaml")


# -------- Custom Actions --------
class TellAbout(Action):
    def run(self, message, user_id, context: Dict):
        resp = requests.get("http://classifier:8585/get_document/" + str(message))
        print(resp)
        return Answer("ща всё будет")


# -------- Register Actions --------
where_is_skill.register_action("tell_about_obj", TellAbout)
