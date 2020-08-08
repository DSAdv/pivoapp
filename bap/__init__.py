from datetime import datetime

from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user


from bap.config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
admin = Admin(app, index_view=AdminIndexView())
login = LoginManager(app)
login.login_view = 'login'

from bap import routes, models, errors


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@login.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


class UserModel(ModelView):
    column_list = ("username", "email", "about_me", "last_seen")


class BeerModel(ModelView):
    column_filters = ("price", "title", "source", "ean")
    # "column_name": [("db_value", "display_value"), ...]
    # column_choices = {
    #     'source': [
    #         ('furshet', 'Фуршет'),
    #         ('auchan', 'Ашан'),
    #         ('megamarket', 'Mega Markt'),
    #         ('novus', 'Novus'),
    #         ('metro', 'Metro'),
    #     ]
    # }
    column_searchable_list = ("title",)
    column_sortable_list = ['timestamp', 'price']
    column_default_sort = [('timestamp', True), ('price', True)]

    # def is_accessible(cls):
    #     return current_user.is_authenticated


admin.add_view(UserModel(models.User, db.session))
admin.add_view(BeerModel(models.BeerPosition, db.session))
