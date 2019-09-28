"""
Модуль для запуска Intent Classification As A Serivce
"""
import flask
import logging
from intent_classifier import IntentClassifier
from decouple import config
CLASSIFIER = "CLASSIFIER"
logging.basicConfig(
    format='%(levelname)s: [%(asctime)s.%(msecs)03d] {} %(name)s '
 '%(filename)s:%(funcName)s:%(lineno)s: %(message)s'.format("CLASSIFIER_WEB_SERVICE"),
 datefmt='%Y-%m-%d %H:%M:%S', level="DEBUG")
log = logging.getLogger(__name__)

app = flask.Flask(__name__)
app.config[CLASSIFIER] = IntentClassifier()

def get_settings():
    app.config["HOST_ADDRESS"] = config('IC_FLASK_ADDRESS', default="0.0.0.0", cast=str)
    app.config["HOST_PORT"] = config('IC_FLASK_PORT', default="8585", cast=int)
    app.config["DEBUG"] = config('IC_FLASK_DEBUG', default=False, cast=bool)

@app.route("/get_event/<query>", methods=["GET"])
def get_event(query):
    log.info("get_event: IN")
    if not query:
        log.warning("get_event: empty query!")
        return "Empty query", 401
    log.debug("get_event: PARSING QUERY: " + str(query))
    result = flask.jsonify(app.config[CLASSIFIER].predict_event(query))
    log.warning("get_event: return prediction: " + str(result))
    return result, 200


@app.route("/get_document/<query>", methods=["GET"])
def get_document(query):
    log.info("get_document: IN")
    if not query:
        log.warning("get_document: empty query!")
        return "Empty query", 401
    log.debug("get_document: PARSING QUERY: " + str(query))
    result = flask.jsonify(app.config[CLASSIFIER].predict_document(query))
    log.warning("get_document: return prediction: " + str(result))
    return result, 200


@app.route("/get_navigation/<query>", methods=["GET"])
def get_navigation(query):
    log.info("get_navigation: IN")
    if not query:
        log.warning("get_navigation: empty query!")
        return "Empty query", 401
    log.debug("get_navigation: PARSING QUERY: " + str(query))
    result = flask.jsonify(app.config[CLASSIFIER].predict_all(query))
    log.warning("get_navigation: return prediction: " + str(result))
    return result, 200


if __name__ == '__main__':
    logging.info("RUNNING FROM MAIN SCRIPT")
    get_settings()
    app.run(app.config["HOST_ADDRESS"], app.config["HOST_PORT"], debug=app.config["DEBUG"])

