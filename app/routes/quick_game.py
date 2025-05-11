from flask import Blueprint, render_template, request, session, url_for
from ..utils import generate_valid_coordinates, calculate_distance
import random

bp = Blueprint('quick_game', __name__)


@bp.route('/quick-game', methods=['GET', 'POST'])
def quick_game():
    """Быстрая игра (доступна даже для неавторизованных пользователей)"""

    # Если метод POST (пользователь отправил данные), то проверяем их
    if request.method == 'POST':
        lat, lng = map(float, (request.form['guess_lat'], request.form['guess_lng']))
        real_lat, real_lng = session['real_lat'], session['real_lng']
        dist = calculate_distance(real_lat, real_lng, lat, lng)
        return render_template('quick_result.html',
                               real_lat=real_lat, real_lng=real_lng,
                               guess_lat=lat, guess_lng=lng,
                               distance=dist)

    # Если метод GET, то просто отдаем страницу с игрой
    real_lat, real_lng = generate_valid_coordinates()
    session['real_lat'], session['real_lng'] = real_lat, real_lng
    return render_template('quick_game.html',
                           real_lat=real_lat, real_lng=real_lng,
                           map_size=random.randint(7, 12))
