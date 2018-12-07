import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from App import app, db, bcrypt
from App.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateResturantForm, update_resturantForm
# importing models
from App.models import Address, Customer, FavoriteList, Label, MenuItem,Restaurant_FavoriteList, Menu, Restaurant, RestaurantOwner, Review, Restaurant_Label, User
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route("/")
#def index():
#	return render_template("index.html", title = 'Index')

@app.route("/home")
def home():
	return render_template("home.html", title = 'Home')


@app.route("/about")
def about():
	return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		address = Address(streetAddress = form.streetAddress.data, unitNumber = form.unitNumber.data, city = form.city.data, state = form.state.data, zipCode = form.zipCode.data, country = form.country.data)
		db.session.add(address)
		db.session.commit()
		user = User(firstName = form.firstName.data, lastName = form.lastName.data, address_id = address.id, username = form.username.data, email = form.email.data, password = hashed_password, type=form.type.data)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('login'))
#picture_file= url_for('static', filename='profile_pics/' + resturant.photo)
	return render_template('register.html', title='Register',form=form)

def save_picture_restaurant(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/restaurant_pics', picture_fn)
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn


@app.route("/creatRestaurant", methods=['GET', 'POST'])
#@login_required
def createRestaurant():
	form = CreateResturantForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture_restaurant(form.picture.data)
		address = Address(streetAddress = form.streetAddress.data, unitNumber = form.unitNumber.data, city = form.city.data, state = form.state.data, zipCode = form.zipCode.data, country = form.country.data)
		db.session.add(address)
		db.session.commit()
		pictureFile = save_picture_restaurant(form.picture.data)
		restaurant = Restaurant(name=form.name.data, phoneNumber = form.phoneNumber.data,description = form.description.data, picture = pictureFile, address_id = address.id, restaurantOwner_id = 2)
		db.session.add(restaurant)
		db.session.commit()
		flash('Your restaurant has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('creat_resturant.html', title='CreateRestaurant',form=form)

@app.route("/update_resturant", methods=['GET', 'POST'])
def update_resturant():
	form = update_resturantForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.picture = picture_file
		current_user.name = form.name.data
		current_user.phone_number = form.phone_number.data
		current_user.type = form.type.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('home'))
		form.name.data = current_user.name
		form.phone_number.data = current_user.phone_number
	return render_template('update_resturant.html', title='Account', form=form)



@app.route("/viewRestaurant/<restaurantId>", methods=['GET', 'POST'])
#TODO: @login_required
def viewRestaurant(restaurantId):
	restaurant = Restaurant.query.get_or_404(restaurantId)
	return render_template('viewRestaurant.html', title='Restaurant', restaurant= restaurant)



@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		if form.type.data:
			user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.photo = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	

	return render_template('account.html', title='Account', photo=photo, form=form)
