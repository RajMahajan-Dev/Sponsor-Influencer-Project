from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import timedelta 
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
    app.config['SESSION_COOKIE_SECURE'] = True
    
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from models import User
        db.create_all()


    @login_manager.user_loader
    def load_user(user_id):
        user= User.query.get(int(user_id))
        return user if user else None
    
    from routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from routes import routes as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True , port=9000)