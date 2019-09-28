"""
Скрипт для генерации контента произведения исскуства
"""
from pymongo import MongoClient

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

CONNECTION = MongoClient()
ARTS = CONNECTION['pushkin']['art']

try:
    print("Добавляем элементы датасета!")
    while True:
        print("=========================")
        name = input("Введите название: ")
        art_type = input("Введите тип предмета: ")
        ids = input("Введите id предмета: ")
        author = input("Введите автора предмета: ")
        date = input("Введите дату создания: ")
        audio = input("Введите ссылку на аудио запись: ")
        img = input("Введите ссылку на картинку: ")
        description = input("Введите краткое описание")
        docs = []
        while True:
            command = input("Введите ключевую фразу или Enter для выхода")
            if not command:
                break
            docs.append(command)
        art = {
            DOC_EXTERNAL_IDS: ids,
            DOC_NAME: name,
            DOC_TYPE: art_type,
            DOC_AUTHOR: author,
            DOC_AUDIO: audio,
            DOC_IMG: img,
            DOC_DATE: date,
            DOC_DESCRIPTION: description,
            DOC_DOCS: docs
        }
        print("ADDING: ", art)
        ARTS.insert_one(art)
        print("ADDED")
except KeyboardInterrupt:
    CONNECTION.close()