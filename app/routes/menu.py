from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Game

bp = Blueprint('menu', __name__)


@bp.route('/menu')
@login_required
def menu():
    unfinished = Game.query.filter_by(user_id=current_user.id, score=None).first()
    return render_template('menu.html', unfinished_game=unfinished)


@bp.route('/leaderboard')
def leaderboard():
    top = Game.query.order_by(Game.score.desc()).limit(10).all()
    return render_template('leaderboard.html', games=top)
