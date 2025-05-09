from flask import Flask
from flask_login import LoginManager
from .models import db, User
from .config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import bp as auth_bp
    from .routes.game import bp as game_bp
    from .routes.quick_game import bp as quick_bp
    from .routes.menu import bp as menu_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(quick_bp)
    app.register_blueprint(menu_bp)

    from .api.endpoints import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # необходимо создать БД и все таблицы здесь, т.к при работе gunicorn в run.py она не создастся (точка входа другая)
    with app.app_context():
        db.create_all()

    return app
