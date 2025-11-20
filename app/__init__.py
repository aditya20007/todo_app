import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "..", "todo.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # import models to register with SQLAlchemy
    from . import models

    with app.app_context():
        db.create_all()
        # seed demo data if empty
        if models.Category.query.count() == 0:
            seed_demo(models, db)

    # register blueprints
    from .routes.auth import auth_bp
    from .routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    @app.route("/")
    def index():
        return redirect(url_for("tasks.view_tasks"))

    return app


def seed_demo(models, db):
    # create categories & tasks to resemble your design
    cat_health = models.Category(name="Health", color="#dbeafe", tag="HEALTH")
    cat_work = models.Category(name="Work", color="#dcfce7", tag="WORK")
    cat_mental = models.Category(name="Mental Health", color="#fce7f3", tag="MENTAL")
    cat_other = models.Category(name="Others", color="#f3f4f6", tag="OTHER")
    db.session.add_all([cat_health, cat_work, cat_mental, cat_other])
    db.session.commit()

    # sample user
    user = models.User(username="demo", email="demo@example.com")
    user.set_password("demo123")
    db.session.add(user)
    db.session.commit()

    tasks = [
        models.Task(title="Drink 8 glasses of water", description="Stay hydrated", done=False, owner=user, category=cat_health),
        models.Task(title="Edit the PDF", description="Make final edits", done=False, owner=user, category=cat_work),
        models.Task(title="Read a book", description='Finish reading "The Great Gatsby"', done=True, owner=user, category=cat_mental),
        models.Task(title="Exercise", description="Go for a 30-minute run", done=False, owner=user, category=cat_health),
    ]
    db.session.add_all(tasks)
    db.session.commit()
