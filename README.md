# alliance-it

Приложение включает в себя:
- **Backend1** (Django/DRF)
- **Backend2** (Django/DRF)
- **Frontend** (React)
- **База данных** (PostgreSQL с PostGIS)
- **Кеширование** (Redis)
- **Очереди задач** (Celery)
- **Брокер сообщений** (Kafka)
- **Логирование и мониторинг** (ELK Stack)
- **Документация API** (Swagger UI)
- **Администрирование базы данных** (pgAdmin)

---

## Требования

1. Docker и Docker Compose.
2. Свободные порты: ```5432, 6379, 8000, 8001, 3000, 8080, 5550, 5601, 9200, 5004```

---

## Запуск проекта

1. Клонируйте репозиторий:
```bash
  git clone https://github.com/SophiaShilkina/alliance-it.git
```
2. Запустите проект:
```bash
  docker-compose up --build
```
3. После запуска сервисы будут доступны по следующим адресам:
- Backend 1: http://localhost:8000
- Backend 2: http://localhost:8001
- Frontend: http://localhost:3000
- Swagger UI: http://localhost:8080
- pgAdmin: http://localhost:5550
- Kibana (ELK): http://localhost:5601

---

# Описание сервисов

## pgAdmin

### URL: http://localhost:5050

- Логин: ```admin@gmail.com```
- Пароль: ```admin```

### Add New Server:

General:
- Name: ```GIS```

Connection:
- Host name/address: ```db```
- Port: ```5432```
- Maintenance database: ```gis```
- Username: ```admin```
- Password: ```admin```

### Примеры использования:

**Просмотр таблиц:**     
Servers → GIS → Databases → gis → Schemas → public → Tables

**SQL-запросы:**     
...

