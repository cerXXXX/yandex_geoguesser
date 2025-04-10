from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Game, Round
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import random
import datetime
import requests

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        nickname = request.form['nickname']

        if password != confirm:
            flash('Пароли не совпадают.')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован.')
            return redirect(url_for('register'))

        if User.query.filter_by(nickname=nickname).first():
            flash('Никнейм уже занят!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, nickname=nickname)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for('menu'))
        else:
            flash('Неверные учетные данные.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/menu')
@login_required
def menu():
    print('Authenticated:', current_user.is_authenticated)
    print('Remembered:', current_user.is_authenticated and '_remember' in request.cookies)
    unfinished_game = Game.query.filter_by(user_id=current_user.id, score=None).first()
    return render_template('menu.html', unfinished_game=unfinished_game)


@app.route('/start_game')
@login_required
def start_game():
    game = Game(user_id=current_user.id, date=datetime.datetime.now())
    db.session.add(game)
    db.session.commit()
    session['game_id'] = game.id
    return redirect(url_for('game'))


@app.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    if request.method == 'POST':
        guess_lat = float(request.form['guess_lat'])
        guess_lng = float(request.form['guess_lng'])
        real_lat = session.get('real_lat')
        real_lng = session.get('real_lng')

        distance = calculate_distance(real_lat, real_lng, guess_lat, guess_lng)
        points = calculate_points(distance)

        round_entry = Round(
            game_id=session['game_id'],
            real_lat=real_lat,
            real_lng=real_lng,
            guess_lat=guess_lat,
            guess_lng=guess_lng,
            distance=distance,
            points=points
        )
        db.session.add(round_entry)
        db.session.commit()

        return redirect(url_for('round_result', round_id=round_entry.id))

    real_lat, real_lng = generate_valid_coordinates()
    session['real_lat'] = real_lat
    session['real_lng'] = real_lng

    # TODO: Добавить API Яндекса для получения снимков
    return render_template('game.html', real_lat=real_lat, real_lng=real_lng)


@app.route('/round_result/<int:round_id>')
@login_required
def round_result(round_id):
    round_entry = Round.query.get(round_id)
    return render_template('round_result.html', round_entry=round_entry)


@app.route('/finish_game')
@login_required
def finish_game():
    game_id = session.get('game_id')
    if not game_id:
        return redirect(url_for('menu'))

    rounds = Round.query.filter_by(game_id=game_id).all()
    total_score = sum(r.points for r in rounds)

    print(game_id)
    game = Game.query.get(game_id)
    print(game)
    game.score = total_score
    db.session.commit()

    return render_template('game_result.html', score=total_score)


@app.route('/leaderboard')
def leaderboard():
    top_games = Game.query.order_by(Game.score.desc()).limit(10).all()
    return render_template('leaderboard.html', games=top_games)


@app.route('/quick-game', methods=['GET', 'POST'])
def quick_game():
    if request.method == 'POST':
        guess_lat = float(request.form['guess_lat'])
        guess_lng = float(request.form['guess_lng'])
        real_lat = session.get('real_lat')
        real_lng = session.get('real_lng')

        distance = calculate_distance(real_lat, real_lng, guess_lat, guess_lng)

        return render_template('quick_result.html', real_lat=real_lat, real_lng=real_lng, guess_lat=guess_lat,
                               guess_lng=guess_lng, distance=distance)

    # Генерируем координаты случайным образом
    real_lat, real_lng = generate_valid_coordinates()
    session['real_lat'] = real_lat
    session['real_lng'] = real_lng

    return render_template('quick_game.html', real_lat=real_lat, real_lng=real_lng)


def generate_valid_coordinates():
    """
    Генерация случайных координат на планете Земля.
    Здесь можно добавить проверку на корректность снимка.
    """
    while True:
        lat = random.uniform(-40, 60)  # избегаем полюсов
        lng = random.uniform(-10, 40)

        # Можем проверить координаты на доступность, если есть API
        if validate_coordinates(lat, lng):
            return lat, lng


def validate_coordinates(lat, lng):
    """
    Проверка валидности координат (доступность спутникового снимка)
    """
    url = f"https://static-maps.yandex.ru/1.x/?ll={lng},{lat}&z=15&size=450,450&l=sat"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200 and b'error' not in response.content:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def calculate_distance(lat1, lng1, lat2, lng2):
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаем таблицы при запуске сервера
    app.run(debug=True)
