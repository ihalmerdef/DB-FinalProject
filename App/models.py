from datetime import datetime
from App import db, login_manager
from flask_login import UserMixin
from functools import partial #for using the query_factory
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)

@login_manager.user_loader
def load_user(user_id):
	result = Customer.query.get(int(user_id))
	result = RestaurantOwner.query.get(int(user_id))
	print(type(result))
	return result

class Address(db.Model):
	__table__ = db.Model.metadata.tables['address']

class Customer(db.Model, UserMixin):
	__table__ = db.Model.metadata.tables['customer']

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

class RestaurantOwner(db.Model, UserMixin):
	__table__ = db.Model.metadata.tables['restaurantOwner']

class Review(db.Model):
	__table__ = db.Model.metadata.tables['review']

class Photos(db.Model):
	__table__ = db.Model.metadata.tables['photos']

class Restaurant_Label(db.Model):
	__table__ = db.Model.metadata.tables['restaurant_label']

class Restaurant_FavoriteList(db.Model):
	__table__ = db.Model.metadata.tables['restaurant_favoriteList']
