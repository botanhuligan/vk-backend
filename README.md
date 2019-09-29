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
- image2vector - сервис идентификации артефактов (произведений искусств) demo134.foxtrot.vkhackathon.com:9918
- voice - STT-TTS сервер с реализацией от Google demo134.foxtrot.vkhackathon.com:9316/tts + demo134.foxtrot.vkhackathon.com:9316/stt
- icaas - Intent Classification As A Service - Сервис интент классификации и Поиска релевантных документов (BERT + KNN) demo134.foxtrot.vkhackathon.com:9316/get_navigation/<query>
- engine - Диалоговый движок
- skills - репозиторий описания скилов
VK Mini Apps CLient - Клиентская реализация с кросс-сервисным взаимодействием
Message Server - Сервис обмена сообщений на технологии Long Pooling (http://demo134.foxtrot.vkhackathon.com:9082/)
MosaicServer - Сервис генерирования изображения из нескольких картин (http://demo134.foxtrot.vkhackathon.com:9082/ image:file)

Все модули обернуты в Docker  файлы и запускаются от docker-compose

