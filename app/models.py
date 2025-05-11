from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """Модель пользователя"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    nickname = db.Column(db.String(64), unique=True, nullable=False)
    avatar = db.Column(db.String(200), nullable=True)


class Game(db.Model):
    """Модель игры"""

    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime)
    score = db.Column(db.Integer)

    user = relationship('User', backref='game')


class Round(db.Model):
    """Модель раунда"""

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    real_lat = db.Column(db.Float, nullable=False)
    real_lng = db.Column(db.Float, nullable=False)
    guess_lat = db.Column(db.Float, nullable=False)
    guess_lng = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    points = db.Column(db.Integer, nullable=False)
