# Intent Classification As a Service

# Установка
ICaaS устанавливается вместе со всеми сервисами через `docker-compose`

- Установите зависимости
```
sudo apt install docker docker-compose
```
- перейдите в корневую директорию
```
cd /path/to/the/project
```
- Запустите сборку проекта
```
docker-compose build
```
- Запустите проект
```
docker-compose up
```
- Для установки тестовых данных - выполните команды
```
docker ps # ищем  ID сервиса под именем vk-backend_classifier
docker exec {container_id} python3 icaas/load_fixrures.py
```