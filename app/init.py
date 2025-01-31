from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from itsdangerous import URLSafeSerializer
import os


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://website:password123@localhost/website'

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg','jpeg', 'png'}

    db.init_app(app)

    from .auth import auth as auth_blueprint
    from .route import route as route_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='')
    app.register_blueprint(route_blueprint, url_prefix='')

    from .models import User, Role

    with app.app_context():
        db.create_all()
        if not Role.query.filter_by(name='Owner').first():
            db.session.add(Role(name='Owner'))
        if not Role.query.filter_by(name='Staff').first():
            db.session.add(Role(name='Staff'))
        if not Role.query.filter_by(name='Customer').first():
            db.session.add(Role(name='Customer'))
        db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
