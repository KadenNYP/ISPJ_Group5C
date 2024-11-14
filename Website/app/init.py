from flask import Flask
from auth import apps
from routes import main


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'

    app.register_blueprint(apps)
    app.register_blueprint(main)

    return app


App = create_app()

if __name__ == '__main__':
    App.run(debug=False)

