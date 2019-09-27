from flask import Flask, request, abort, jsonify
from engine import Dispatcher, Message
from log import log

app = Flask(__name__)


class MyServer:
    def __init__(self):
        self.init = "Hello"
        self.dispatcher = Dispatcher()
        self.dispatcher.add_skill("static/skill.yaml")
        self.dispatcher.build_events("static/events.yaml")


my_server = MyServer()


@app.route("/")
def init():
    return my_server.init


NO_MESSAGE_IN_REQUEST = "No message in request"


@app.route("/message", methods=["POST"])
def message_post():
    if not request.json:
        log.error(NO_MESSAGE_IN_REQUEST)
        abort(400, {"error": NO_MESSAGE_IN_REQUEST})

    message = Message(request.json)
    try:
        my_server.dispatcher.run(message)
    except Exception as exception:
        log.error(exception)
        abort(500, {"error": exception})

    return "OK"


if __name__ == "__main__":
    app.run("0.0.0.0", 9080)
