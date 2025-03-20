# alliance-it

Приложение включает в себя:
- **Backend1** (Django/DRF)
- **Backend2** (Django/DRF)
- **Frontend** (React)
- **База данных** (PostgreSQL с PostGIS)
- **Кеширование** (Redis)
- **Очереди задач** (Celery)
- **Брокер сообщений** (Kafka, Zookeeper)
- **Логирование и мониторинг** (ELK Stack)
- **Документация API** (Swagger UI)
- **Администрирование базы данных** (pgAdmin)

## Требования

1. Docker и Docker Compose.
2. Свободные порты: ```5432, 6379, 8000, 8001, 3000, 8080, 5550, 5601, 9200, 5004```

## Запуск проекта

1. Клонируйте репозиторий:
```bash
  git clone https://github.com/SophiaShilkina/alliance-it.git
```
2. Запустите проект:
```bash
  docker-compose up --build
```
3. Примените миграции:
```bash
  docker-compose exec backend1 python manage.py migrate
````
4. Создайте администратора:
```bash
  docker-compose exec backend1 python manage.py createsuperuser
```
5. После запуска сервисы будут доступны по следующим адресам:
- Backend 1: http://localhost:8000
- Backend 2: http://localhost:8001
- Frontend: http://localhost:3000
- Swagger UI: http://localhost:8080
- pgAdmin: http://localhost:5550
- Kibana: http://localhost:5601

---

# Описание сервисов

## pgAdmin

- URL: http://localhost:5550
- Логин: ```admin@gmail.com```
- Пароль: ```admin```

### Add New Server:

General:
- Name: ```GIS```

Connection:
- Host name/address: ```db```
- Port: ```5432```
- Maintenance database: ```gis```
- Username: ```postgres```
- Password: ```1234```

### Query Tool Workspace:

- Existing Server: ```GIS```
- Database: ```gis```
- User: ```postgres```
- Password: ```1234```

### Примеры использования:

**Просмотр таблиц:**     
Servers → GIS → Databases → gis → Schemas → public → Tables

**SQL-запросы:**   
- Получение всех полигонов: 
```
SELECT * FROM polygons_polygon;
```
- Получение всех полигонов с координатами в читаемом формате:
```
SELECT id, name, ST_AsText(coordinates) AS coordinates, crosses_antimeridian FROM polygons_polygon;
```
- Получение всех полигонов и связных полей:
```
SELECT 
    p.id AS polygon_id,
    p.name AS polygon_name,
    ST_AsText(p.coordinates) AS polygon_coordinates,
    p.crosses_antimeridian,
    u.id AS user_id,
    u.username AS user_username
FROM 
    polygons_polygon AS p
LEFT JOIN 
    polygons_polygonuserassignment AS pua ON p.id = pua.polygon_id
LEFT JOIN 
    auth_user AS u ON pua.user_id = u.id;
```

## Предусмотренные ошибки:
### ```PolygonSerializer```
В процессе валидации полигона в методе ```validate_coordinates``` предусмотрены следующие ошибки:

- **Недостаточное количество точек**  
_Ошибка:_ ```raise serializers.ValidationError("Полигон должен содержать как минимум 3 точки.")```    
_Условие возникновения:_ Количество переданных координат полигона строго меньше 3.      
_Решение:_ Убедитесь, что полигон содержит как минимум 3 неодинаковые точки.


- **Замкнутый полигон с недостаточным количеством точек**     
_Ошибка:_ ```raise serializers.ValidationError("Полигон должен содержать как минимум 3 незамкнутые точки.")```  
_Условие возникновения:_ Полигон состоит ровно из 3 точек, где первая и последняя точки совпадают (полигон замкнут).    
_Решение:_ Убедитесь, что полигон содержит как минимум 3 уникальные точки, если он не замкнут.


- **Повторяющиеся координаты**  
_Ошибка:_ ```raise serializers.ValidationError("Полигон не должен содержать повторяющиеся координаты, кроме 
замыкающих точек.")```  
_Условие возникновения:_ В полигоне обнаружены повторяющиеся координаты, за исключением случая, когда первая и 
последняя точки совпадают (замыкание полигона).     
_Решение:_ Убедитесь, что все координаты полигона уникальны, кроме первой и последней точки, если полигон замкнут.

**Дополнительные примечания**   
_Замыкание полигона:_ Если полигон не замкнут (первая и последняя точки не совпадают), метод **автоматически** добавляет 
первую точку в конец списка координат для замыкания. Это действие логируется с помощью ```logger.info(f"Полигон не был 
замкнут. Первая точка {first_point} добавлена в конец для замыкания.")```