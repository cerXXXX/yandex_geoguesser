from flask import Blueprint, request, jsonify, current_app
from ..models import db, User, Game, Round
import datetime

api_bp = Blueprint('api', __name__)


@api_bp.before_request
def require_api_key():
    # разрешаем публичный endpoint для показа ключа, если он у вас есть
    if request.endpoint and request.endpoint.endswith('show_api_key'):
        return

    token = request.headers.get('X-API-KEY', '')
    if not token or token != current_app.config['API_KEY']:
        return jsonify({'error': 'Unauthorized'}), 401


# Пользователи
@api_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify([{'id': u.id, 'email': u.email, 'nickname': u.nickname}
                    for u in User.query.all()])


@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    u = User.query.get_or_404(user_id)
    return jsonify({'id': u.id, 'email': u.email, 'nickname': u.nickname})


@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    for f in ('email', 'password', 'nickname'):
        if f not in data:
            return jsonify(error=f"Missing field {f}"), 400
    user = User(email=data['email'],
                password=data['password'],
                nickname=data['nickname'])
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id), 201


# Игры
@api_bp.route('/games', methods=['GET'])
def get_games():
    return jsonify([{'id': g.id, 'user_id': g.user_id,
                     'date': g.date.isoformat(),
                     'score': g.score} for g in Game.query.all()])


@api_bp.route('/games', methods=['POST'])
def create_game():
    data = request.get_json() or {}
    if 'user_id' not in data:
        return jsonify(error="Missing user_id"), 400
    g = Game(user_id=data['user_id'],
             date=datetime.datetime.now(),
             score=data.get('score'))
    db.session.add(g)
    db.session.commit()
    return jsonify(id=g.id), 201


# Раунды
@api_bp.route('/rounds', methods=['GET'])
def get_rounds():
    return jsonify([{'id': r.id, 'game_id': r.game_id,
                     'real_lat': r.real_lat, 'real_lng': r.real_lng,
                     'guess_lat': r.guess_lat, 'guess_lng': r.guess_lng,
                     'distance': r.distance, 'points': r.points}
                    for r in Round.query.all()])


@api_bp.route('/rounds', methods=['POST'])
def create_round():
    data = request.get_json() or {}
    required = ['game_id', 'real_lat', 'real_lng', 'guess_lat', 'guess_lng']
    if not all(f in data for f in required):
        return jsonify(error="Missing fields"), 400
    dist = calculate_distance(data['real_lat'], data['real_lng'],
                              data['guess_lat'], data['guess_lng'])
    pts = calculate_points(dist)
    r = Round(game_id=data['game_id'],
              real_lat=data['real_lat'], real_lng=data['real_lng'],
              guess_lat=data['guess_lat'], guess_lng=data['guess_lng'],
              distance=dist, points=pts)
    db.session.add(r)
    db.session.commit()
    return jsonify(id=r.id), 201


# === Сброс и пересоздание базы данных ===
@api_bp.route('/reset-db', methods=['POST'])
def reset_db():
    """
    Полный сброс: удаляем все таблицы и создаём заново.
    ВНИМАНИЕ: удаляет все данные!
    """

    db.drop_all()
    db.create_all()
    return jsonify(message="Database has been reset and recreated."), 200
