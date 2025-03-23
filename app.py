from flask import Flask, render_template_string, request, redirect, session
import random
import requests
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Для работы сессий


# === Главная страница ===
@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Быстрая игра GeoGuesser</title>
        <style>
            body { font-family: Arial; text-align: center; background: #f5f5f5; margin: 0; padding: 50px; }
            button { padding: 20px 40px; font-size: 20px; background-color: #4CAF50; color: white; border: none; border-radius: 10px; cursor: pointer; }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h1>Добро пожаловать в Быструю игру GeoGuesser!</h1>
        <a href="/quick-game"><button>Начать игру</button></a>
    </body>
    </html>
    """)


# === Быстрая игра ===
@app.route('/quick-game', methods=['GET', 'POST'])
def quick_game():
    if request.method == 'POST':
        guess_lat = float(request.form['guess_lat'])
        guess_lng = float(request.form['guess_lng'])
        real_lat = session.get('real_lat')
        real_lng = session.get('real_lng')

        distance = calculate_distance(real_lat, real_lng, guess_lat, guess_lng)

        return redirect(
            f"/quick-result?real_lat={real_lat}&real_lng={real_lng}&guess_lat={guess_lat}&guess_lng={guess_lng}&distance={distance}")

    # Генерация координат
    real_lat, real_lng = generate_valid_coordinates()
    session['real_lat'] = real_lat
    session['real_lng'] = real_lng

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Быстрая игра</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body { margin: 0; font-family: Arial; background: #222; color: white; }
            .game-container { display: flex; height: 100vh; }
            .left-panel, .right-panel { flex: 1; display: flex; justify-content: center; align-items: center; }
            .left-panel { background: #111; }
            .right-panel { background: #1e1e1e; flex-direction: column; }
            .guess-map { width: 90%; height: 500px; border-radius: 10px; }
            .guess-button { margin-top: 20px; padding: 15px 30px; font-size: 18px; background-color: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="game-container">
            <div class="left-panel">
                <img id="satelliteImage" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div class="right-panel">
                <div id="map" class="guess-map"></div>
                <form id="guess-form" method="post">
                    <input type="hidden" name="guess_lat" id="guess_lat">
                    <input type="hidden" name="guess_lng" id="guess_lng">
                    <button type="submit" disabled id="submit-button" class="guess-button">Подтвердить выбор</button>
                </form>
            </div>
        </div>

        <script>
            const realLat = {{ real_lat }};
            const realLng = {{ real_lng }};

            function loadSatelliteImage() {
                const container = document.querySelector('.left-panel');
                const width = Math.min(Math.floor(container.clientWidth), 650);
                const height = Math.min(Math.floor(container.clientHeight), 450);
                const url = `https://static-maps.yandex.ru/1.x/?ll=${realLng},${realLat}&z=15&size=${width},${height}&l=sat`;
                document.getElementById('satelliteImage').src = url;
            }

            window.addEventListener('resize', loadSatelliteImage);
            window.addEventListener('load', loadSatelliteImage);

            var map = L.map('map').setView([20, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            var marker;

            map.on('click', function(e) {
                const lat = e.latlng.lat.toFixed(6);
                const lng = e.latlng.lng.toFixed(6);

                if (marker) {
                    marker.setLatLng([lat, lng]);
                } else {
                    marker = L.marker([lat, lng]).addTo(map);
                }

                document.getElementById('guess_lat').value = lat;
                document.getElementById('guess_lng').value = lng;
                document.getElementById('submit-button').disabled = false;
            });
        </script>
    </body>
    </html>
    """, real_lat=real_lat, real_lng=real_lng)


# === Результат быстрой игры ===
@app.route('/quick-result')
def quick_result():
    real_lat = float(request.args.get('real_lat'))
    real_lng = float(request.args.get('real_lng'))
    guess_lat = float(request.args.get('guess_lat'))
    guess_lng = float(request.args.get('guess_lng'))
    distance = float(request.args.get('distance'))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Результат</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body { margin: 0; font-family: Arial; background: #222; color: white; }
            .game-container { display: flex; height: 100vh; }
            .left-panel, .right-panel { flex: 1; display: flex; justify-content: center; align-items: center; flex-direction: column; }
            .left-panel { background: #111; }
            .right-panel { background: #1e1e1e; }
            .guess-map { width: 90%; height: 500px; border-radius: 10px; }
            .guess-button { margin-top: 20px; padding: 15px 30px; font-size: 18px; background-color: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="game-container">
            <div class="left-panel">
                <div>
                    <h2>Результат быстрой игры</h2>
                    <p>Твоя отметка была на расстоянии:</p>
                    <h1>{{ distance | round(2) }} км</h1>

                    <div>
                        <a href="/quick-game"><button class="guess-button">Играть ещё раз</button></a>
                        <a href="/"><button class="guess-button">В меню</button></a>
                    </div>
                </div>
            </div>
            <div class="right-panel">
                <div id="result-map" class="guess-map"></div>
            </div>
        </div>

        <script>
            var map = L.map('result-map').setView([{{ real_lat }}, {{ real_lng }}], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

            var realMarker = L.marker([{{ real_lat }}, {{ real_lng }}]).addTo(map).bindPopup('Правильное место').openPopup();
            var guessMarker = L.marker([{{ guess_lat }}, {{ guess_lng }}]).addTo(map).bindPopup('Твоя отметка');

            var line = L.polyline([
                [{{ real_lat }}, {{ real_lng }}],
                [{{ guess_lat }}, {{ guess_lng }}]
            ], { color: 'red' }).addTo(map);

            var group = new L.featureGroup([realMarker, guessMarker]);
            map.fitBounds(group.getBounds(), { padding: [50, 50] });
        </script>
    </body>
    </html>
    """, real_lat=real_lat, real_lng=real_lng, guess_lat=guess_lat, guess_lng=guess_lng, distance=distance)


# === Вспомогательные функции ===
def generate_valid_coordinates():
    """Генерация координат с проверкой доступности снимка"""
    for attempt in range(20):  # не более 20 попыток
        lat = random.uniform(-40, 60)
        lng = random.uniform(-10, 40)

        if validate_coordinates(lat, lng):
            print(f"Координаты найдены: lat={lat}, lng={lng}")
            return lat, lng

    # Если после 20 попыток не нашли — возвращаем последние с предупреждением
    print("Не удалось найти валидные координаты. Возвращаю последние.")
    return lat, lng


def validate_coordinates(lat, lng):
    """Проверяем, что снимок существует на сервере Яндекс"""
    url = f"https://static-maps.yandex.ru/1.x/?ll={lng},{lat}&z=15&size=450,450&l=sat"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200 and b'error' not in response.content:
            return True
    except requests.RequestException as e:
        print(f"Ошибка запроса Yandex API: {e}")
    return False


def calculate_distance(lat1, lng1, lat2, lng2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


if __name__ == '__main__':
    app.run(debug=True)
