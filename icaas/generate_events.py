"""
Скрипт для генерации ивентов
"""
from pymongo import MongoClient

EVENT_IDS = "_id"
EVENT_NAME = 'name'
EVENT_EMBEDDINGS = 'embeddings'
EVENT_PHRASES = 'phrases'

CONNECTION = MongoClient()
EVENTS = CONNECTION['pushkin']['events']

try:
    print("Добавляем элементы датасета!")
    while True:
        name = input("Введите название: ")
        phrases = []
        while True:
            command = input("Введите ключевую фразу или Enter для выхода")
            if not command:
                break
            phrases.append(command)
        event = {
                EVENT_NAME: name,
                EVENT_PHRASES: phrases
            }
        print("ADDING: ", event)
        EVENTS.insert_one(event)
except KeyboardInterrupt:
    CONNECTION.close()