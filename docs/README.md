# NotGeoGuesser

NotGeoGuesser — это веб-приложение на Flask в жанре Geoguessr, где игроки угадывают локацию по спутниковому снимку и отмечают ёё на карте. Поддерживается полная регистрация, авторизация, сохранение результатов, быстрый раунд без регистрации, REST API и контейнеризация через Docker.

---

## 📂 Структура проекта

```
project-root/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── utils.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── game.py
│   │   ├── quick_game.py
│   │   ├── menu.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py
│   ├── cli.py
│   ├── secret.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── game.html
│   │   ├── game_result.html
│   │   ├── leaderboard.html
│   │   ├── login.html
│   │   ├── menu.html
│   │   ├── quick_game.html
│   │   ├── quick_result.html
│   │   ├── register.html
│   │   ├── round_result.html
│   ├── static/
│   │   ├── favicon.ico
│   │   └── style.css
├── .secret/
│   ├── api_key.txt
├── docs/
│   ├── Описание.txt
│   ├── ТЗ.txt
│   └── README.md
├── dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
└── README.md
```

---

## ⚙️ Быстрый старт (Docker)

1. `git clone https://github.com/your-user/NotGeoGuesser.git`
2. `cd NotGeoGuesser`
3. `docker compose up -d --build`
4. `docker compose exec app flask show-api-key`

---

## 🐍 Локально (Python)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask show-api-key
flask run
```

---

## 🔐 API

Все эндпоинты REST API доступны по пути `/api/...` и требуют наличия заголовка `X-API-KEY` со значением вашего секретного ключа.

### Получение API-ключа

При первом старте приложения автоматически генерируется токен и сохраняется в файле `.secret/api_key.txt`. Чтобы узнать ключ:

```bash
# Если вы в Docker-контейнере:
docker compose exec app flask show-api-key

# Локально в виртуальном окружении:
flask show-api-key
```

### Пример заголовка

```
X-API-KEY: <ваш-ключ>
```

### Список основных эндпоинтов

| Метод | URL             | Описание                    |
| ----- | --------------- | --------------------------- |
| GET   | /api/users      | Список всех пользователей   |
| GET   | /api/users/<id> | Получить пользователя по ID |
| POST  | /api/users      | Создать пользователя        |
| GET   | /api/games      | Список всех игр             |
| POST  | /api/games      | Создать новую игру          |
| GET   | /api/rounds     | Список всех раундов         |
| POST  | /api/rounds     | Создать новый раунд         |
| POST  | /api/reset-db   | Сброс и пересоздание БД     |

(Все POST-запросы принимают и возвращают JSON.)
### Пример использования

#### Через `curl`

```bash
curl -H "X-API-KEY: YOUR_API_KEY" http://localhost:5000/api/users
```

#### Через Python

```python
import requests

API_KEY = 'YOUR_API_KEY'
headers = {'X-API-KEY': API_KEY}

response = requests.get('http://localhost:5000/api/users', headers=headers)
print(response.json())
```

---

## 🖇️ Функции

* Регистрация / Вход
* Основной меню / Продолжение игры
* Игра c оценкой расстояния
* Быстрая игра (без бд)
* Таблица лидеров
* Защищённое REST API

---

## 🚀 Продакшн

1. Установить Docker, Docker Compose
2. `git clone` или `scp`
3. `docker compose up -d --build`
4. Настроить HTTPS/прокси (напр. NGINX)

---

## 🙏 Автор

**NotGeoGuesser** создан для учебных и развлекательных целей. 

MIT License
