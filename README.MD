Python 3.9

1. Создайте суперпользователя коммандой:
```
python manage.py createsuperuser 
```
2. Для наполнения базы тестовыми данными запустите команду:
```
python manage.py loaddata data.json
```

3. Для записи ваших изменений в тестовую базу
```
python manage.py dumpdata > fixtures/data.json
```
4. На сервере необходимо будет создать файл `.env` с переменными:
```
DEBUG=false
DATABASE_URL=psql://user:un-githubbedpassword@127.0.0.1:8458/database - пример
```

5. Для упрощенного запуска с помощью docker-compose
```
docker-compose -f docker-compose-local.yaml up
```

6. Проверка подключения к БД на сервере
```

python manage.py wait_for_db
```

7. Быстрое создание суперпользователя
```
python manage.py initadmin
```


