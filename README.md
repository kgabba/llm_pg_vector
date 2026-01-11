# 🚀 RAG API + Auth (FastAPI + PostgreSQL + pgvector)

Backend-сервис, который объединяет:

- 🔐 регистрацию/авторизацию через **JWT в cookie**
- 🧩 роли (`moderator`, `admin`, `user`)
- 📄 загрузку PDF/DOCX → извлечение текста
- 🧠 RAG-модель на основе:
  - PostgreSQL + pgvector
  - text-embedding-3-small
  - gpt-4o-mini

Проект полностью контейнеризован (Docker Compose): поднимается API, PostgreSQL и pgAdmin.

---

## 🧱 Стек технологий

- **Python 3.11**
- **FastAPI**, Uvicorn  
- **PostgreSQL 15**, расширение **pgvector**
- **LangChain**: ChatOpenAI, OpenAIEmbeddings  
- **PyPDF2**, python-docx  
- **Docker / docker-compose**  
- **pgAdmin 4**

---

## 📦 Архитектура (docker-compose)

| Сервис        | Описание                        | Порт |
|---------------|----------------------------------|------|
| `api_app`     | FastAPI backend                  | 8000 |
| `postgres_db` | PostgreSQL + pgvector            | 5432 |
| `pg_admin`    | Веб-интерфейс PostgreSQL         | 5050 |

---

## 🗄️ Структура БД

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    roles TEXT[],
    hash_psw TEXT NOT NULL,
    session_token TEXT
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding VECTOR(1536)
);
```

---

## 🚀 Запуск проекта

1. **Создайте файл .env**
```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=mydb
API_KEY=sk-...
```

2. **Поднимите контейнеры**
```bash
docker compose up --build
```

После запуска:

- API → http://localhost:8000/docs
- pgAdmin → http://localhost:5050
- PostgreSQL → localhost:5432

---

## 🔐 Авторизация и роли

Используется JWT, который кладётся в cookie:

- `/auth/login` → устанавливает cookie
- `/bd/reg_user` → регистрация
- `/bd/update_roles` → управление доступом (только moderator)

**Роли:**

| Роль | Возможности |
|------|-------------|
| user | делать RAG-запросы (`/llm/ask`) |
| admin | загружать данные (`/llm/embed`, `/llm/embed_file`) |
| moderator | назначать/удалять роль user |

---

## 📚 Основные эндпоинты API

### ⭐ Регистрация
```bash
POST /bd/reg_user
```
**Body:**
```json
{
  "username": "test",
  "password": "123",
  "password_repeat": "123"
}
```

### ⭐ Логин
```bash
POST /auth/login
```
⟶ Ставит `jwt_personal_session_token` в cookie.

### ⭐ Управление ролями (moderator)
```bash
POST /bd/update_roles
```
**Form-data:**

| Поле | Значение |
|------|----------|
| username | у кого изменить роль |
| action | `add` или `remove` |

---

## 🧩 Работа с эмбеддингами

### ⭐ Загрузка текста (admin)
```bash
POST /llm/embed
```
**Body:**
```json
{
  "text": "длинный текст"
}
```
**Результат:**

1. текст режется на чанки
2. создаются эмбеддинги
3. записывается в БД

### ⭐ Загрузка PDF/DOCX (admin)
```bash
POST /llm/embed_file
```
**multipart/form-data:**
```javascript
file: <PDF или DOCX>
```
**Поддержка:**

- PDF → извлечение текста
- DOCX → параграфы + таблицы

---

## 🧠 RAG-запросы

```bash
POST /llm/ask
```
**Body:**
```json
{
  "text": "вопрос"
}
```
**Пайплайн:**

1. делаем эмбеддинг вопроса
2. ищем top-k ближайших чанков через pgvector
3. формируем строгий промпт
4. если данных нет → "Нет такой информации в базе"

**Пример ответа:**
```json
{
  "answer": "…",
  "context_used": ["чанк1", "чанк2"]
}
```

---

## 🛠 Планы развития

- Telegram-бот (использующий API)
- Метаданные для файлов
- Асинхронный PostgreSQL (asyncpg)
- SQLAlchemy
- Веб-админка для управления пользователями
