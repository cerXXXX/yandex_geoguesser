from flask import Blueprint, request, jsonify
from ..models import db, User, Game, Round
import datetime

api_bp = Blueprint('api', __name__)


# Users
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
    db.session.add(user);
    db.session.commit()
    return jsonify(id=user.id), 201


# Games
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
    db.session.add(g);
    db.session.commit()
    return jsonify(id=g.id), 201


# Rounds
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
    db.session.add(r);
    db.session.commit()
    return jsonify(id=r.id), 201
