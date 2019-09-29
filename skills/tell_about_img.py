from typing import Dict

import requests

from engine import Skill, Action, Answer

tell_about_img = Skill("static/tell_about_img.yaml")


# -------- Custom Actions --------
class TellAbout(Action):
    def run(self, message, user_id, context: Dict):
        resp = requests.get("http://classifier:8585/get_document/" + str(message))
        context["doc"] = resp.json()
        if context["doc"]:
            return Answer(
                "Картина {1} автора {0}. Рассказать подробнее?".format(context["doc"]["author"], context["doc"]["name"]),
                "{2} - безумно интересное прозиведение. Автор картины {0}. {1} Рассказать подробнее?".format(
                    context["doc"]["author"], context["doc"]["description"], context["doc"]["name"]
                ),
                url_img=context["doc"]["img"]
            )
        else:
            self.event("RESTART", user_id, message)
            return Answer("К сожалению, я не знаю такого произведения. Попробуй ещё." )


class TellMoreAbout(Action):
    def run(self, message, user_id, context: Dict):
        if context["doc"]:
            return Answer(
                "Картина {1} автора {0}.".format(context["doc"]["author"], context["doc"]["name"]),
                "Запускаю",
                url_img=context["doc"]["img"],
                url_voice=context["doc"]["audio"]
            )
        else:
            self.event("RESTART", user_id, message)
            return Answer("К сожалению я потерял нить разговора. Попробуй ещё.")


# -------- Register Actions --------
tell_about_img.register_action("tell_about_obj", TellAbout)
tell_about_img.register_action("tell_more_about_obj", TellMoreAbout)
