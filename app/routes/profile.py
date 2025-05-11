from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from ..models import db, User
import os

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# Куда будем сохранять аватары
UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS


@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def edit():
    """Отображение и обработка формы редактирования профиля пользователя."""

    # Если пришел POST-запрос (отправлена форма), обрабатываем данные и сохраняем пользователя
    if request.method == 'POST':
        # Смена e-mail
        new_email = request.form.get('email')
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Этот e-mail уже занят.', 'error')
            else:
                current_user.email = new_email

        # Смена пароля
        pwd = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if pwd:
            if pwd == confirm:
                current_user.password = generate_password_hash(pwd)
            else:
                flash('Пароли не совпадают.', 'error')

        # Загрузка аватара
        file = request.files.get('avatar')
        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{current_user.id}_" + file.filename)
            save_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            os.makedirs(save_dir, exist_ok=True)
            path = os.path.join(save_dir, filename)
            file.save(path)
            current_user.avatar = f"{UPLOAD_FOLDER}/{filename}"

        db.session.commit()
        flash('Профиль сохранён.', 'success')
        return redirect(url_for('profile.edit'))

    return render_template('profile.html', user=current_user)
