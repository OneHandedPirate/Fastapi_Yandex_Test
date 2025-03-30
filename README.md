### YANDEX MUSIC TEST
<hr>

<details>
<summary>ТЗ</summary>
Реализовать сервис по загрузке аудио-файлов от пользователей, используя FastAPI, SQLAlchemy и Docker. Пользователи могут давать файлам имя в самом API.
Авторизацию пользователей реализовать через Яндекс.
Файлы хранить локально, хранилище использовать не нужно.
Использовать асинхронный код.
БД - PostgreSQL 16.

Ожидаемый результат:
1. Готовое API с возможностью авторизации через Яндекс с последующей аутентификацией к запросам через внутренние токены API.
Доступные эндпоинты: авторизация через яндекс, обновление внутреннего access_token; получение, изменение данных пользователя, удаление пользователя от имени суперпользователя; получение информации о аудио файлах пользователя: название файлов и путь в локальной хранилище.
2. Документация по развертыванию сервиса и БД в Docker.
</details>

### Запуск

Выполнить команды:
```
git clone https://github.com/OneHandedPirate/Fastapi_Yandex_Test.git
cd Fastapi_Yandex_Test
make create_env
```

В созданный `.env` файл нужно вписать: 
1. `YANDEX__CLIENT_ID` и `YANDEX__CLIENT_SECRET` приложения Яндекса, а так же в поле `Redirect URI для веб-сервисов` настроек приложения вписать `http://localhost:8000/api/auth/callback`
2. Так же вписать в переменную `ADMIN_EMAILS` почты админов (суперюзеров) (список строк в двойных кавычках). При создании пользователя с почтой из этого списка он автоматически становится суперюзером.
3. (опционально) Можно так же вписать `FILES__MAX_SIZE` - максимальный размер загружаемого файла (в байтах) (по умолчанию 50 Мб) и `FILES__ALLOWED_TYPES` - список допустимых для загрузки MIME-типов файлов (по умолчанию - ["audio/mpeg", "audio/wav", "audio/ogg", "audio/flac"], т.е. аудиофайлы)
4. (опционально) Время жизни access и refresh токенов можно регулировать переменными `AUTH__ACCESS_TOKEN_EXPIRE_MINUTES` и `AUTH__REFRESH_TOKEN_EXPIRE_MINUTES` - время жизни токенов в минутах (по умолчанию - 15 и 10080 соответственно) и `AUTH__SECRET_KEY` - ключ приложения (по умолчанию -`not_a_secret`) 
5. Можно поменять `DB__OUTER_PORT` (по умолчанию - 5432) - внешний порт БД для удобного просмотра (через DBeaver например)

Выполнить `make start` - поднимет docker compose с приложением и БД.
Приложение будет доступно на `http://localhost:8000`.


### Список эндпоинтов

- auth:
  
  - `api/auth/login` [GET] - логин через яндекс (редиректит на страницу Yandex-auth, выполнять непосредственно из браузера, из `/docs` не работает).
  - `api/auth/callback` [GET] - на этот эндпоинт редиректит при успешном входе через Yandex. При первом входе автоматически создается новый юзер в БД из данных, получаемых от Yandex.
    
    - Пример ответа:
      ```
      {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGVmNTFlZjgtODBlZC00MjQ5LTkxZTktMTUyYWMwNGM0OGM0IiwiZXhwIjoxNzQzMzA1MjcxLCJ0eXBlIjoiYWNjZXNzIn0.kVgQGJY8dm7HZs5ubuHgYmUZCELJwpY5ojsmUlbJGSg",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGVmNTFlZjgtODBlZC00MjQ5LTkxZTktMTUyYWMwNGM0OGM0IiwiZXhwIjoxNzQzOTA5MTcxLCJ0eXBlIjoicmVmcmVzaCJ9.ptj1J0Jglgy-phrNWahh8zgnDoE-orgmqw3KrAGkSwA"
      }
      ``` 
  - `api/auth/refresh` [POST] - обновление access_token.  
    
    - Пример тела запроса:
        ```
        {
           "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGVmNTFlZjgtODBlZC00MjQ5LTkxZTktMTUyYWMwNGM0OGM0IiwiZXhwIjoxNzQzOTA5MTcxLCJ0eXBlIjoicmVmcmVzaCJ9.ptj1J0Jglgy-phrNWahh8zgnDoE-orgmqw3KrAGkSwA" 
        }
        ```
    - Пример ответа:  
        ```
      {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGVmNTFlZjgtODBlZC00MjQ5LTkxZTktMTUyYWMwNGM0OGM0IiwiZXhwIjoxNzQzMzA1MjcxLCJ0eXBlIjoiYWNjZXNzIn0.kVgQGJY8dm7HZs5ubuHgYmUZCELJwpY5ojsmUlbJGSg"
      }
      ``` 

!Все эндпоинты ниже требуют `access_token` в заголовке `Authorization` (`Authorization: Bearer <access_token>`)

- users:
    
    - `api/users/my-info` [GET] - информация о пользователе.
      
      - Пример ответа:
        ```
        {
          "id": "8ef51ef8-80ed-4249-91e9-152ac04c48c4",
          "yandex_id": "129102881",
          "username": "OneHandedPirate",
          "first_name": "D",
          "last_name": "L",
          "email": "plagueismkii@yandex.ru",
          "is_admin": true
        }
        ```
    - `api/users/{user_id}` [GET] - информация о пользователе по его id в БД.
      - Пример ответа:
        ```
        {
          "id": "8ef51ef8-80ed-4249-91e9-152ac04c48c4",
          "yandex_id": "129102881",
          "username": "OneHandedPirate",
          "first_name": "D",
          "last_name": "L",
          "email": "plagueismkii@yandex.ru",
          "is_admin": true
        }
        ```
    - `api/users/{user_id}` [PATCH] - обновление информации пользователя (если пользователя не суперюзер он может обновлять только свою информацию). Можно обновлять только поля `username`, `first_name` и `last_name`.
      - Пример тела запроса:
        ```
        {
          "last_name": "La"
        }
        ```
      - Пример ответа: 
        ```
        {
          "id": "8ef51ef8-80ed-4249-91e9-152ac04c48c4",
          "yandex_id": "129102881",
          "username": "OneHandedPirate",
          "first_name": "D",
          "last_name": "La",
          "email": "plagueismkii@yandex.ru",
          "is_admin": true
        }
        ```
    - `api/users/{user_id}` [DELETE] - удаление юзера. Удалять могут только суперюзеры. Суперюзеров нельзя удалять. При удалении юзера удаляются так же все файлы и записи файлов в БД.
    
- files

  - `api/files/upload` [POST] - загрузка файлов через `form-data`. `file` - файл, `name` - имя файла для БД (максимальная длина 100 символов). Имя непосредственно загруженного файла формируется из `uuid4` и расширения исходного файла если оно есть. Переданный в запросе `name` сохраняется в соответствующем поле в БД. `path` в ответе - абсолютный путь в файлу.
    - Пример ответа:
      ```
      {
        "id": "844580ba-6d83-4822-8259-dc5ffeec25f2",
        "name": "Some valid name",
        "path": "/app/files/8ef51ef8-80ed-4249-91e9-152ac04c48c4/cf19ac22-865c-4cb5-9844-91ffbf312498.mp3"
      }
      ```
  - `api/files/my-files` [GET] - получение списка файлов юзера.
    - Пример ответа:
      ```
      [
        {
          "id": "844580ba-6d83-4822-8259-dc5ffeec25f2",
          "name": "Some valid name",
          "path": "/app/files/8ef51ef8-80ed-4249-91e9-152ac04c48c4/cf19ac22-865c-4cb5-9844-91ffbf312498.mp3"
        }
      ]
      ```
  - `api/files/{user_id}` - [GET] - получение списка файлов юзера по его id. Только для суперюзеров (если id не совпадает с id текущего юзера).
    - Пример ответа:
        ```
        [
          {
            "id": "844580ba-6d83-4822-8259-dc5ffeec25f2",
            "name": "Some valid name",
            "path": "/app/files/8ef51ef8-80ed-4249-91e9-152ac04c48c4/cf19ac22-865c-4cb5-9844-91ffbf312498.mp3"
          }
        ]
        ```