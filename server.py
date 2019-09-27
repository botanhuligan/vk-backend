from flask import Flask
app = Flask(__name__)


class MyServer:
    def __init__(self):
        self.init = "Hello"


my_server = MyServer()


@app.route("/")
def init():
    return my_server.init


if __name__ == "__main__":
    app.run("0.0.0.0", 9080)
