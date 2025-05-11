from flask import Flask
from flask_login import LoginManager
from .models import db, User
from .config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    """Создание приложения."""

    app = Flask(__name__)

    # регистрация команду для получения ключа API
    from .secret import get_api_key
    from .cli import register_cli
    register_cli(app)

    # конфигурация приложения
    app.config.from_object(Config)

    # инициализация БД
    db.init_app(app)
    login_manager.init_app(app)

    # инициализация пользователей
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # регистрация blueprints
    from .routes.auth import bp as auth_bp
    from .routes.game import bp as game_bp
    from .routes.quick_game import bp as quick_bp
    from .routes.menu import bp as menu_bp
    from .routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(quick_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(profile_bp)

    # регистрация API
    from .api.endpoints import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # необходимо создать БД и все таблицы здесь, т.к при работе gunicorn в run.py она не создастся (точка входа другая)
    with app.app_context():
        db.create_all()

    return app
