from flask import Blueprint, request, jsonify
from models import db, User, Game, Round

api_bp = Blueprint('api', __name__, url_prefix='/api')


# --- Пользователи ---

@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'nickname': u.nickname
    } for u in users])


@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'email': user.email,
        'nickname': user.nickname
    })


@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password', 'nickname')):
        return jsonify({'error': 'Missing required fields'}), 400
    new_user = User(
        email=data['email'],
        password=data['password'],  # Предполагается, что хеширование происходит на стороне клиента
        nickname=data['nickname']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id}), 201


# --- Игры ---

@api_bp.route('/games', methods=['GET'])
def get_games():
    games = Game.query.all()
    return jsonify([{
        'id': g.id,
        'user_id': g.user_id,
        'date': g.date.isoformat(),
        'score': g.score
    } for g in games])


@api_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify({
        'id': game.id,
        'user_id': game.user_id,
        'date': game.date.isoformat(),
        'score': game.score
    })


@api_bp.route('/games', methods=['POST'])
def create_game():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
    new_game = Game(
        user_id=data['user_id'],
        date=data.get('date'),  # Предполагается, что дата передается в формате ISO
        score=data.get('score')
    )
    db.session.add(new_game)
    db.session.commit()
    return jsonify({'id': new_game.id}), 201


# --- Раунды ---

@api_bp.route('/rounds', methods=['GET'])
def get_rounds():
    rounds = Round.query.all()
    return jsonify([{
        'id': r.id,
        'game_id': r.game_id,
        'real_lat': r.real_lat,
        'real_lng': r.real_lng,
        'guess_lat': r.guess_lat,
        'guess_lng': r.guess_lng,
        'distance': r.distance,
        'points': r.points
    } for r in rounds])


@api_bp.route('/rounds/<int:round_id>', methods=['GET'])
def get_round(round_id):
    round_entry = Round.query.get_or_404(round_id)
    return jsonify({
        'id': round_entry.id,
        'game_id': round_entry.game_id,
        'real_lat': round_entry.real_lat,
        'real_lng': round_entry.real_lng,
        'guess_lat': round_entry.guess_lat,
        'guess_lng': round_entry.guess_lng,
        'distance': round_entry.distance,
        'points': round_entry.points
    })


@api_bp.route('/rounds', methods=['POST'])
def create_round():
    data = request.get_json()
    required_fields = ('game_id', 'real_lat', 'real_lng', 'guess_lat', 'guess_lng', 'distance', 'points')
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    new_round = Round(
        game_id=data['game_id'],
        real_lat=data['real_lat'],
        real_lng=data['real_lng'],
        guess_lat=data['guess_lat'],
        guess_lng=data['guess_lng'],
        distance=data['distance'],
        points=data['points']
    )
    db.session.add(new_round)
    db.session.commit()
    return jsonify({'id': new_round.id}), 201
