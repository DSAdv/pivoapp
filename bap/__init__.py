from datetime import datetime

from flask import Flask, url_for, render_template, send_from_directory, redirect
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user


from bap.config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

admin = Admin(app, index_view=AdminIndexView())


from bap import routes, models, errors


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@login.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.BeerPosition, db.session))
