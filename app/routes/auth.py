from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, User

bp = Blueprint('auth', __name__)


@bp.route('/')
def index():
    """Если пришли в корень, то перенаправляем на страницу авторизации."""

    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации."""

    # Если пользователь уже авторизован, то перенаправляем на главную.
    if current_user.is_authenticated:
        return redirect(url_for('menu.menu'))

    # Если метод POST (пользователь отправил форму), то регистрируем пользователя и перенаправляем на страницу входа.
    if request.method == 'POST':
        # получаем данные из формы
        email, pw, confirm = request.form['email'], request.form['password'], request.form['confirm']
        nickname = request.form['nickname']

        # проверяем данные
        if pw != confirm:
            flash('Пароли не совпадают.')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован.')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(nickname=nickname).first():
            flash('Никнейм уже занят.')
            return redirect(url_for('auth.register'))

        # создаем пользователя и сохраняем в БД
        user = User(email=email,
                    password=generate_password_hash(pw),
                    nickname=nickname)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа."""

    # Если пользователь уже авторизован, то перенаправляем на главную.
    if current_user.is_authenticated:
        return redirect(url_for('menu.menu'))

    # Если метод POST (пользователь отправил форму), то проверяем данные и авторизуем.
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user, remember=bool(request.form.get('remember')))
            return redirect(url_for('menu.menu'))
        flash('Неверные учетные данные.')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    """Страница выхода."""

    logout_user()
    return redirect(url_for('auth.login'))
