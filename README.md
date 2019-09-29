# Art Mira

Описание проекта

Основной репозиториb проекта: 
ArtMira - Backend https://github.com/botanhuligan/vk-backend
VK Mini Apps CLient - https://github.com/botanhuligan/vk-client
Message Server - https://github.com/botanhuligan/vk-message-server
MosaicServer - https://github.com/botanhuligan/vk-mosaic-server

Язык реализации Backend - Python
Реализация Frontend - ReactJS (VK Mini Apps)
База данных - MongoDB

 Проект реализован на микросервисной архитектуре с основным сервисом -
 ArtMira - Backend со следующими функциями модулями:
- image2vector - сервис идентификации артефактов (произведений искусств)
- voice - STT-TTS сервер с реализацией от Google
- icaas - Intent Classification As A Service - Сервис интент классификации и Поиска релевантных документов (BERT + KNN)
- engine - Диалоговый движок
- skills - репозиторий описания скилов
VK Mini Apps CLient - Клиентская реализация с кросс-сервисным взаимодействием
Message Server - Сервис обмена сообщений на технологии Long Pooling
MosaicServer - Сервис генерирования изображения из нескольких картин

Все модули обернуты в Docker  файлы и запускаются от docker-compose

