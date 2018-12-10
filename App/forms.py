from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from App import db
from App.models import User, Address, Label, MenuItem,FavoriteList, Menu, Restaurant, Review, Restaurant_Label,Restaurant_FavoriteList 
from wtforms.fields.html5 import DateField

#Global scope
ratingChoices = [('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5')]

#User Forms
class RegistrationForm(FlaskForm):
	firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
	lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	phoneNumber = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	streetAddress = StringField('Street Address', validators=[DataRequired(), Length(min=10, max=50)])
	unitNumber = IntegerField('Unit Number', validators=[])
	city = StringField('City', validators = [DataRequired()])
	state = StringField('State', validators = [DataRequired()])
	zipCode = IntegerField('Zip code', validators = [DataRequired()])
	country = StringField('Country', validators = [DataRequired()])
	type = StringField('User Type', validators = [DataRequired()])
	submit = SubmitField('Sign Up')
	
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	type = SelectField('User Type', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
	

class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')
	
	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one.')
#Search Forms
class SearchForm(FlaskForm):
	searchString = StringField('Search query', validators = [DataRequired(), Length(min =2, max= 50)])
	submit = SubmitField('Search')
#----------------------------------------------------------
#Restaurant Forms
class CreateResturantForm(FlaskForm):
	name = StringField('Restaurant Name', validators=[DataRequired(), Length(min=2, max=20)])
	phoneNumber = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
	description= StringField('Restaurant Description', validators=[DataRequired(), Length(min=5, max=200)])
	picture = FileField('Upload a Restuarant Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])
	streetAddress = StringField('Street Address', validators=[DataRequired(), Length(min=10, max=50)])
	unitNumber = IntegerField('Unit Number', validators=[])
	city = StringField('City', validators = [DataRequired()])
	state = StringField('State', validators = [DataRequired()])
	zipCode = IntegerField('Zip code', validators = [DataRequired()])
	country = StringField('Country', validators = [DataRequired()])
	#type = SelectField('User Type', validators = [DataRequired()])
	submit = SubmitField('Add Restuarant!')
	
	def validate_name(self, name):
		restaurant = Restaurant.query.filter_by(name=name.data).first()
		if restaurant:
			raise ValidationError('That name is taken. Please choose a different one.')


class updateRestaurantForm(FlaskForm):
	name = StringField('Restaurant Name', validators=[DataRequired(), Length(min=2, max=20)])
	phoneNumber = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=20)])
	#type= StringField('Food Type', validators=[DataRequired(), Length(min=2, max=20)])
	description= StringField('Restaurant Description', validators=[DataRequired(), Length(min=5, max=200)])
	picture = FileField('Upload a Restuarant Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])
	
	submit = SubmitField('Update!')
	
	def validate_name(self, name):
		restaurant = Restaurant.query.filter_by(name=name.data).first()
		if restaurant:
			raise ValidationError('That name is taken. Please choose a different one.')
#----------------------------------------------------------

#Review Forms
class ReviewForm(FlaskForm):
	rating = SelectField('Rating (out of 5)', choices = ratingChoices, validators=[DataRequired()])
	comment = StringField('Review', validators=[DataRequired(), Length(min=2, max=200)])
	submit = SubmitField('Add Review')
#----------------------------------------------------------

#Favorite List Forms
class FavoriteListForm(FlaskForm):
	name = StringField('List name', validators=[DataRequired()])
#----------------------------------------------------------

# Menu Forms
class MenuForm(FlaskForm):
	menuName = StringField('Menu name', validators=[DataRequired(), Length(min = 2, max = 20)])
	submit = SubmitField('Add Menu')
#----------------------------------------------------------

# MenuItem Forms
class MenuItemForm(FlaskForm):
	name = StringField('Item name', validators = [DataRequired()])
	description = StringField('Item description', validators = [DataRequired()])
	price = DecimalField('Price', validators = [DataRequired()])
	phote = FileField('Upload a Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])
	submit = SubmitField('Add item')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	type = StringField('User Type', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

