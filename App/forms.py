from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from App import db
from App.models import Address, Customer, Favorite_List, Label, MenuItem,Favorite_List, Menu, Restaurant, RestaurantOwner, Review, Restaurant_Label
from wtforms.fields.html5 import DateField

class RegistrationForm(FlaskForm):
	firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
	lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	streetAddress = StringField('Street Address', validators=[DataRequired(), Length(min=10, max=50)])
	unitNumber = IntegerField('Unit Number', validators=[])
	city = StringField('City', validators = [DataRequired()])
	state = StringField('City', validators = [DataRequired()])
	zipCode = IntegerField('Zip code', validators = [DataRequired()])
	country = StringField('country', validators = [DataRequired()])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		customer = Customer.query.filter_by(username=username.data).first()
		if customer:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		customer = Customer.query.filter_by(email=email.data).first()
		if customer:
			raise ValidationError('That email is taken. Please choose a different one.')

class creat_resturantForm(FlaskForm):
	name = StringField('Restaurant Name', validators=[DataRequired(), Length(min=2, max=20)])
	phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=20)])
	description= StringField('Restaurant description', validators=[DataRequired(), Length(min=2, max=20)])
	picture = FileField('Upload a Restuarant Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])

	submit = SubmitField('Create!')

	def validate_name(self, name):
		restaurant = Restaurant.query.filter_by(name=name.data).first()
		if restaurant:
			raise ValidationError('That name is taken. Please choose a different one.')

class update_resturantForm(FlaskForm):
	name = StringField('Restaurant Name', validators=[DataRequired(), Length(min=2, max=20)])
	phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=20)])
	type= StringField('Food Type', validators=[DataRequired(), Length(min=2, max=20)])
	picture = FileField('Upload a Restuarant Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])

	submit = SubmitField('Update!')

	def validate_name(self, name):
		if name.data != current_user.name:
			restaurant = Restaurant.query.filter_by(name=name.data).first()
			if restaurant:
				raise ValidationError('That username is taken. Please choose a different one.')



class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
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
