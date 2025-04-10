from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    # Добавляем связь с пользователем!
    user = relationship('User', backref='games')


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    real_lat = db.Column(db.Float)
    real_lng = db.Column(db.Float)
    guess_lat = db.Column(db.Float)
    guess_lng = db.Column(db.Float)
    distance = db.Column(db.Float)
    points = db.Column(db.Integer)
