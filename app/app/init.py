import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://website:password123@localhost/website'
    db.init_app(app)

    from .auth import auth as auth_blueprint
    from .route import route as route_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='')
    app.register_blueprint(route_blueprint, url_prefix='')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app