"""
Скрипт для загрузки фикстурок
"""
import os
from pymongo import MongoClient
import json

DOC = "doc"
DOC_IDS = "_id"
DOC_EXTERNAL_IDS = "external_ids"
DOC_DOCS = "docs"
DOC_NAME = 'name'
DOC_TYPE = 'type'
DOC_AUTHOR = 'author'
DOC_DATE = 'date'
DOC_AUDIO = 'audio'
DOC_IMG = 'img'
DOC_DESCRIPTION = 'description'

EVENT = 'event'
EVENT_IDS = "_id"
EVENT_NAME = 'name'
EVENT_EMBEDDINGS = 'embeddings'
EVENT_PHRASES = 'phrases'

HOST_ADDRESS = "mongodb"
HOST_PORT = 27017

CONNECTION = MongoClient(HOST_ADDRESS, HOST_PORT)
ARTS = CONNECTION['pushkin']['art']
EVENTS = CONNECTION['pushkin']['events']


def save_to_json():
    result = {}
    result[DOC] = []
    result[EVENT] = []
    for document in ARTS.find():
        result[DOC].append({
            DOC_EXTERNAL_IDS: document[DOC_EXTERNAL_IDS],
            DOC_DOCS: document[DOC_DOCS],
            DOC_NAME: document[DOC_NAME],
            DOC_TYPE: document[DOC_TYPE],
            DOC_AUTHOR: document[DOC_AUTHOR],
            DOC_AUDIO: document[DOC_AUDIO],
            DOC_IMG: document[DOC_IMG],
            DOC_DESCRIPTION: document[DOC_DESCRIPTION],
        })
    for event in EVENTS.find():
        result[EVENT].append({
            EVENT_NAME: event[EVENT_NAME],
            EVENT_PHRASES: event[EVENT_PHRASES]
        })
    with open(os.path.join(os.path.dirname(__file__), 'fixtures.json'), "w") as stream:
        stream.write(json.dumps(result, ensure_ascii=False))


def load_from_json():
    with open(os.path.join(os.path.dirname(__file__), 'fixtures.json'), "r") as stream:
        result = json.load(stream)
    if EVENTS.find_one():
        for event in EVENTS.find():
            EVENTS.delete_one(event)
    for event in result[EVENT]:
        EVENTS.insert_one({
            EVENT_NAME: event[EVENT_NAME],
            EVENT_PHRASES: event[EVENT_PHRASES]
        })
    if ARTS.find_one():
        for event in ARTS.find():
            ARTS.delete_one(event)
    for document in result[DOC]:
        ARTS.insert_one({
            DOC_EXTERNAL_IDS: document[DOC_EXTERNAL_IDS],
            DOC_DOCS: document[DOC_DOCS],
            DOC_NAME: document[DOC_NAME],
            DOC_TYPE: document[DOC_TYPE],
            DOC_AUTHOR: document[DOC_AUTHOR],
            DOC_AUDIO: document[DOC_AUDIO],
            DOC_IMG: document[DOC_IMG],
            DOC_DESCRIPTION: document[DOC_DESCRIPTION],
        })


if __name__ == '__main__':
    load_from_json()