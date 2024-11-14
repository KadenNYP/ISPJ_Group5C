import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


pymysql.install_as_MySQLdb()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'

    from auth import auth as auth_blueprint
    from route import route as route_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='')
    app.register_blueprint(route_blueprint, url_prefix='')

    return app

app = create_app()

app.run(debug=True)

