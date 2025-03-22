# Прикладной Python. HW3

#### Автор: Кульжик Степан

### [Ссылка на развернутый сервис](https://appliedpython-hw3.onrender.com/docs#/)


## Описание API

### default
`GET /health` - проверка работоспособност сервиса    

### Auth
`POST /auth/register` - регистрация нового пользователя
`POST /auth/login` - логин пользователя (на этом этапе пользователь получает token)

### Links
`POST /links/shorten` - создает короткую ссылку (можно указывать `alias`, `expires_at`) \
`GET /{short_code}` - возвращает оригинальную URL по короткой ссылке \
`DELETE /links/{short_code}` - удаляет короткую ссылку \
`PUT /links/{short_code}` - обновляет URL в короткой ссылке \
`GET /links/{short_code}/stats` - возвращает стаститку по короткой ссылке \
`GET /{short_link}/info` - возвращает информацию по короткой ссылке \
`GET /links/search` - ищет оригинальную URL 

## Примеры запросов

`POST /links/sharten`: \
Запрос: 
``` 
{
  "original_url": "https://www.youtube.com/watch?v=YXoeRtd8PeU",
  "custom_alias": "podcast",
  "expires_at": "2025-03-22T19:31:49.688Z"
}
``` 


Ответ: 
```
{
  "original_url": "https://www.youtube.com/watch?v=YXoeRtd8PeU",
  "short_code": "veAmNG",
  "click_count": 0,
  "created_at": "2025-03-22T18:32:10",
  "last_accessed": null
}
```

`GET /{short_code}`: \
Ответ: 
```
{
  "original_url": "https://www.youtube.com/watch?v=YXoeRtd8PeU",
  "created_at": "2025-03-22T18:32:10",
  "click_count": 1,
  "last_accessed": "2025-03-22T18:32:22.820648"
}
```

`DELETE /links/{short_code}`: \
Ответ:
```
{
  "detail": "Deleted"
}
```

`PUT /links/{short_code}`: \
Запрос: 
```
{
  "original_url": "https://www.youtube.com/watch?v=vC5cHjcgt5g"
}
```

Ответ: 
```
{
  "original_url": "https://www.youtube.com/watch?v=vC5cHjcgt5g",
  "short_code": "veAmNG",
  "click_count": 1,
  "created_at": "2025-03-22T18:32:10",
  "last_accessed": "2025-03-22T18:32:22.820648"
}
```

`GET /links/{short_code}/stats`: \
Ответ:
```
{
  "original_url": "https://www.youtube.com/watch?v=vC5cHjcgt5g",
  "short_code": "veAmNG",
  "click_count": 1,
  "created_at": "2025-03-22T18:32:10",
  "last_accessed": "2025-03-22T18:32:22.820648"
}
```

`GET /links/{short_code}/info`: \
Ответ: 
```
{
  "original_url": "https://www.youtube.com/watch?v=vC5cHjcgt5g",
  "created_at": "2025-03-22T18:32:10",
  "click_count": 1,
  "last_accessed": "2025-03-22T18:32:22.820648",
  "short_code": "veAmNG",
  "custom_alias": "podcast"
}
```

`GET /links/search`: \
Ответ: 
```
[
  {
    "original_url": "https://www.youtube.com/watch?v=vC5cHjcgt5g",
    "short_code": "veAmNG",
    "created_at": "2025-03-22T18:32:10",
    "click_count": 1,
    "last_accessed": "2025-03-22T18:32:22.820648",
    "custom_alias": "podcast"
  }
]
```

## Инструкция по запуску

Сначала устанавливаем зависимости
```
pip install -r requirements.txt
```

Потом запускаем наш сервис:
```
python run.py
```

## Описание БД

### Таблица Users
* `id`: Автоинкрементный первичный ключ 
* `username`: Уникальное имя пользователя для аутентификации
* `email` : Уникальный email адрес
* `password`: Хэшированный пароль
* `created_at`: Временная метка создания пользователя

### Таблица Links:
* `id`: Автоинкрементный первичный ключ
* `short_code`: Сгенерированный короткий код для URL
* `custom_alias`: Опциональный пользовательский алиас для URL
* `original_url`: Оригинальный длинный URL
* `user_id`: Внешний ключ к таблице пользователей (опционально)
* `created_at`: Дата создания ссылки
* `click_count`: Количество переходов по ссылке
* `last_accessed`: Время последнего доступа
* `expires_at`: Опциональная дата истечения срока действия