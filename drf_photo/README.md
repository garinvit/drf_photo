для загрузки БД
```
python3 backend/manage.py migrate
python3 backend/manage.py loaddata db.json 
```
Команда для удаления файлов фотографий которые не используются(остались от тестирования например)
```
python3 backend/manage.py photo_del  удаляет файлы без записи в БД
python3 backend/manage.py photo_del -s показывает все категории файлов. Не удаляет
python3 backend/manage.py photo_del -di удаляет записи в БД у которых нет изображений
```
Либо на тестовом сервере garinv.xyz

Новая версия API v2:

В модели альбом возможно сортировать по полям:

"id", "title", "created_at", "count".

Возможно отключить показ тэгов и фотографий в альбомах
используя GET параметр "display_tags" и "photo_set"
```
http://garinv.xyz/api/v2/album/?photos=false&display_tags=false&ordering=id
```
В модели альбом возможно сортировать по полям:

"id", "title", "created_at", "count".

В модели альбом возможно сортировать по полям:

"id", "title", "created_at".

Так же возможно указать только необходимые теги:
```
http://garinv.xyz/api/v2/album/photo/?tags=3,4&ordering=-created_at
```
Экспорт запросов из postman в файлах:

DRF V2 garinv.xyz.json

DRF V2 localhost.json