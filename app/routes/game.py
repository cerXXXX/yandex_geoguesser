from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, Game, Round
from ..utils import generate_valid_coordinates, calculate_distance, calculate_points
import datetime, random

bp = Blueprint('game', __name__)


@bp.route('/start_game')
@login_required
def start_game():
    game = Game(user_id=current_user.id, date=datetime.datetime.now())
    db.session.add(game)
    db.session.commit()
    session['game_id'] = game.id
    return redirect(url_for('game.game'))


@bp.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    if request.method == 'POST':
        lat, lng = map(float, (request.form['guess_lat'], request.form['guess_lng']))
        real_lat, real_lng = session['real_lat'], session['real_lng']
        dist = calculate_distance(real_lat, real_lng, lat, lng)
        pts = calculate_points(dist)
        rnd = Round(game_id=session['game_id'],
                    real_lat=real_lat, real_lng=real_lng,
                    guess_lat=lat, guess_lng=lng,
                    distance=dist, points=pts)
        db.session.add(rnd)
        db.session.commit()
        return redirect(url_for('game.round_result', round_id=rnd.id))
    real_lat, real_lng = generate_valid_coordinates()
    session['real_lat'], session['real_lng'] = real_lat, real_lng
    return render_template('game.html',
                           real_lat=real_lat, real_lng=real_lng,
                           map_size=random.randint(7, 12))


@bp.route('/round_result/<int:round_id>')
@login_required
def round_result(round_id):
    entry = Round.query.get_or_404(round_id)
    return render_template('round_result.html', round_entry=entry)


@bp.route('/finish_game')
@login_required
def finish_game():
    gid = session.pop('game_id', None)
    if not gid:
        return redirect(url_for('menu.menu'))
    rounds = Round.query.filter_by(game_id=gid).all()
    total = sum(r.points for r in rounds)
    game = Game.query.get(gid)
    game.score = total
    db.session.commit()
    session.pop('real_lat', None)
    session.pop('real_lng', None)
    return render_template('game_result.html', score=total)
