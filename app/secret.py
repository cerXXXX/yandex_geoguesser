import os
import secrets

SECRET_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, '.secret')
API_KEY_FILE = os.path.join(SECRET_DIR, 'api_key.txt')


def get_api_key():
    """
    Возвращает токен, создавая его при первом обращении.
    Файл .secret/api_key.txt не хранится в репозитории.
    """
    os.makedirs(SECRET_DIR, exist_ok=True)
    # Если файла нет — генерируем и сохраняем
    if not os.path.exists(API_KEY_FILE):
        token = secrets.token_hex(32)  # 64-символьный безопасный токен
        with open(API_KEY_FILE, 'w') as f:
            f.write(token)
    else:
        with open(API_KEY_FILE) as f:
            token = f.read().strip()
    return token
