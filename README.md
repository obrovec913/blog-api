
---

# FastAPI Blog API

Этот проект представляет собой API для ведения блога, реализованный на FastAPI и PostgreSQL. API поддерживает аутентификацию, CRUD-операции с постами и расширенные функции, такие как поиск и статистика по пользователям.

## Стек технологий

- **FastAPI**
- **PostgreSQL**
- **Docker Compose**

## Установка и запуск

### Предварительные условия

Убедитесь, что на вашем компьютере установлены:
- **Docker**
- **Docker Compose**

### Шаг 1: Клонирование репозитория

Клонируйте репозиторий проекта:

```bash
git clone https://github.com/obrovec913/blog-api.git
cd glog-api
```
### Шаг 2: Запуск Docker Compose

Запустите сервисы с помощью Docker Compose:

```bash
docker-compose up -d --build
```

### Проверка состояния

После запуска Docker Compose вы сможете проверить работу приложения, открыв в браузере: [http://localhost:8000](http://localhost:8000).

Документация API (Swagger UI) доступна по адресу: [http://localhost:8000/docs](http://localhost:8000/docs).

## Конфигурация Docker Compose

### В Файле `docker-compose.yml`
## Использование API

### 1. Регистрация нового пользователя

```http
POST /register
```

**Пример запроса:**
```json
{
  "username": "newuser",
  "password": "password123"
}
```

### 2. Получение токена доступа

```http
POST /token
```

**Пример запроса:**
```json
{
  "username": "newuser",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "access_token": "<JWT Token>",
  "token_type": "bearer"
}
```

### 3. Получение списка постов

```http
GET /posts
```

**Параметры запроса**:

- `skip`: количество постов для пропуска.
- `limit`: ограничение на количество возвращаемых постов.

### 4. Создание нового поста (требуется токен)

```http
POST /posts
```

**Требуется заголовок авторизации:**

```
Authorization: Bearer <access_token>
```

**Пример запроса:**
```json
{
  "title": "My First Post",
  "content": "This is the content of my post."
}
```

### 5. Обновление поста (требуется токен)

```http
PUT /posts/{id}
```

**Требуется заголовок авторизации:**

```
Authorization: Bearer <access_token>
```

**Пример запроса:**
```json
{
  "title": "Updated Post Title",
  "content": "Updated content of the post."
}
```

### 6. Удаление поста (требуется токен)

```http
DELETE /posts/{id}
```

**Требуется заголовок авторизации:**

```
Authorization: Bearer <access_token>
```

### 7. Поиск постов

```http
GET /posts/search
```

**Параметры запроса:**

- `query`: текст для поиска в заголовке и содержимом постов.
  
### 8. Получение статистики по пользователю

```http
GET /posts/statistics/{user_id}
```

---

## Заключение

Теперь вы можете развернуть и использовать API для ведения блога.