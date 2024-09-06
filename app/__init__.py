from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(Config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config_class)

    db.init_app(app)    
    migrate.init_app(app, db)  # Initialize Flask-Migrate with the app and db
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.main.routes import main
    from app.auth.routes import auth
    from app.rental.routes import rental
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(rental)

    from app.models import Client, Admin

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        return Client.query.get(int(user_id)) or Admin.query.get(int(user_id))

    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
