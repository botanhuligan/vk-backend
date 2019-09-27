import json

import requests
from flask import Flask, request, abort, jsonify

from simple_skill import simple_skill
from engine import Dispatcher, Message
from log import log
import multiprocessing as mp

app = Flask(__name__)

headers = {'Content-type': 'application/json',  # Определение типа данных
           'Accept': 'text/plain',
           'Content-Encoding': 'utf-8'}


class MyServer:
    def __init__(self):
        self.init = "Hello"
        self.dispatcher = Dispatcher()
        self.dispatcher.add_skill(simple_skill)
        self.dispatcher.build_events("static/events.yaml")
        self.dispatcher.set_send_message(self.send_message)
        self.dispatcher.set_send_log(self.send_log)

    def start(self):
        self.dispatcher.start()

    def send_message(self, message):
        requests.post("http://back:9081/say",
                      json.dumps(message),
                      headers=headers)

    def send_log(self, message):
        requests.post("http://back:9081/log",
                      json.dumps(message),
                      headers=headers)

my_server = MyServer()
process = []


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
        my_server.dispatcher.message_handler(message)
    except Exception as exception:
        log.error(exception)
        abort(500, {"error": exception})

    return "OK"


def start_server():
    app.run("0.0.0.0", 9080)


if __name__ == "__main__":
    t1 = mp.Process(target=start_server)
    t2 = mp.Process(target=my_server.start)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
