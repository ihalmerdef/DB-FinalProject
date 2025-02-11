from datetime import datetime
from App import db, login_manager
from flask_login import UserMixin
from functools import partial #for using the query_factory
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	__table_args__ = {'extend_existing': True}
	__table__ = db.Model.metadata.tables['user']
	def __repr__(self):
		return f"User('{self.username}', '{self.email}')"

class Address(db.Model):
	__table__ = db.Model.metadata.tables['address']

class Label(db.Model):
	__table__ = db.Model.metadata.tables['label']

class MenuItem(db.Model):
	__table__ = db.Model.metadata.tables['menuItem']

class FavoriteList(db.Model):
	__table__ = db.Model.metadata.tables['favoriteList']

class Menu(db.Model):
	__table__ = db.Model.metadata.tables['menu']

class Restaurant(db.Model):
	__table__ = db.Model.metadata.tables['restaurant']
	__searchable__ = ['name', 'description']

class Review(db.Model):
	__table__ = db.Model.metadata.tables['review']

class Restaurant_Label(db.Model):
	__table__ = db.Model.metadata.tables['restaurant_label']

class Restaurant_FavoriteList(db.Model):
	__table__ = db.Model.metadata.tables['restaurant_favoriteList']
