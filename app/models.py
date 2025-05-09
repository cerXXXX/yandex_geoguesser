from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    nickname = db.Column(db.String(64), unique=True, nullable=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Integer)


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    real_lat = db.Column(db.Float, nullable=False)
    real_lng = db.Column(db.Float, nullable=False)
    guess_lat = db.Column(db.Float, nullable=False)
    guess_lng = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    points = db.Column(db.Integer, nullable=False)
