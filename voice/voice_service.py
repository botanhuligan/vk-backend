"""
Text to Speech service
"""
import os
import flask
from decouple import config
import logging
from google.cloud import texttospeech
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
log = logging.getLogger(__name__)
logging.basicConfig(
    format='%(levelname)s: [%(asctime)s.%(msecs)03d] {} %(name)s '
 '%(filename)s:%(funcName)s:%(lineno)s: %(message)s'.format("VOICE_SERVICE"),
 datefmt='%Y-%m-%d %H:%M:%S', level="DEBUG")
app = flask.Flask(__name__)
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(os.path.dirname(__file__), config("GOOGLE_APPLICATION_CREDENTIALS", default="OwnResearch-3e4345c8f9be.json", cast=str))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
app.config["TTS_CLIENT"] = texttospeech.TextToSpeechClient()
app.config["STT_CLIENT"] = speech.SpeechClient()
app.config["STT_TTS_HOST"] = config("STT_TTS_HOST", default="0.0.0.0", cast=str)
app.config["STT_TTS_PORT"] = config("STT_TTS_PORT", default="9316", cast=int)

@app.route('/tts', methods=['GET', 'POST'])
def tts():
    if "text" not in flask.request.json:
        return "Text Not Found", 401
    text = flask.request.json.get("text")
    if not text:
        return "Empty text", 401
    synthesis_input = texttospeech.types.SynthesisInput(text=text)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='ru-RU',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.OGG_OPUS)
    response = app.config["TTS_CLIENT"].synthesize_speech(synthesis_input, voice, audio_config)
    with open(os.path.join(os.path.dirname(__file__), 'output.ogg'), 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
    return flask.send_file(os.path.join(os.path.dirname(__file__), 'output.ogg'))


@app.route('/stt', methods=['POST'])
def stt():
    voice = flask.request.files.get("voice")
    if not voice:
        return "Voice empty", 401
    voice.save(os.path.join(os.path.dirname(__file__), 'voice.ogg'))
    with open(os.path.join(os.path.dirname(__file__), 'voice.ogg'), 'rb') as out:
        audio = types.RecognitionAudio(content=out.read())
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=24000,
        language_code='ru-Ru')
    response = app.config["STT_CLIENT"].recognize(config, audio)
    result = response.results[0].alternatives[0].transcript
    return flask.jsonify( {"text": result}) , 200


if __name__ == '__main__':
    app.run(app.config["STT_TTS_HOST"], app.config["STT_TTS_PORT"], debug=True)