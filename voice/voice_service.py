"""
Text to Speech service
"""
import logging
import requests
import flask
from google.cloud import texttospeech

app = flask.Flask()


client = texttospeech.TextToSpeechClient()
synthesis_input = texttospeech.types.SynthesisInput(text="Hello, World!")


@app.route('/tts')
def tts():
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='ru-RU',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.OGG_OPUS)


@app.route('stt')
def stt():
    pass