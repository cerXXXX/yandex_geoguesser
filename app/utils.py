import random
import requests


def generate_valid_coordinates():
    """Генерация случайных координат в заданном диапазоне с проверкой."""
    for _ in range(20):
        lat = random.uniform(-40, 60)
        lng = random.uniform(-10, 40)
        if validate_coordinates(lat, lng):
            return lat, lng
    return lat, lng


def validate_coordinates(lat, lng):
    """Проверка доступности спутникового снимка Яндекс."""
    url = f"https://static-maps.yandex.ru/1.x/?ll={lng},{lat}&z=15&size=450,450&l=sat"
    try:
        r = requests.get(url, timeout=3)
        return r.status_code == 200 and b'error' not in r.content
    except requests.RequestException:
        return False


def calculate_distance(lat1, lng1, lat2, lng2):
    """Эвклидовых на сфере (прибл.)."""
    return ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5 * 111


def calculate_points(distance):
    if distance < 10:
        return 5000
    elif distance < 100:
        return 4000
    elif distance < 500:
        return 3000
    elif distance < 1000:
        return 2000
    else:
        return 1000
