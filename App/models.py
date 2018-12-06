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

class User(db.Model, UserMixin):
	__table_args__ = {'extend_existing': True}
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	photo = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	#posts = db.relationship('Post', backref='authxor', lazy=True)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.photo}')"

class Post(db.Model):
	__table_args__ = {'extend_existing': True}
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}')"

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
