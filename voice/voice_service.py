"""
Text to Speech service
"""
import os
import logging
import flask
from decouple import config
from google.cloud.texttospeech import TextToSpeechClient, types, enums

app = flask.Flask(__name__)
GOOGLE_APPLICATION_CREDENTIALS="voice/OwnResearch-3e4345c8f9be.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config("GOOGLE_APPLICATION_CREDENTIALS", default="voice/OwnResearch-3e4345c8f9be.json", cast=str)
client = TextToSpeechClient()

app.config["CLIENT"] = client



@app.route('/tts')
def tts():
    if "text" not in flask.request.json:
        return "Text Not Found", 401
    text = flask.request.json.get("text")
    if not text:
        return "Empty text", 401
    synthesis_input = types.SynthesisInput(text=text)
    voice = types.VoiceSelectionParams(
        language_code='ru-RU',
        ssml_gender=enums.SsmlVoiceGender.NEUTRAL)
    audio_config = types.AudioConfig(
        audio_encoding=enums.AudioEncoding.OGG_OPUS)
    response = app.config["CLIENT"].synthesize_speech(synthesis_input, voice, audio_config)
    with open(os.path.join(os.path.dirname(__file__), 'output.mp3'), 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
    return flask.send_file(os.path.join(os.path.dirname(__file__), 'output.mp3'))

@app.route('/stt')
def stt():
    pass


if __name__ == '__main__':
    app.run("0.0.0.0", 8989, debug=True)