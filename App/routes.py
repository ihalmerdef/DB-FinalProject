import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from App import app, db, bcrypt
#importing forms
from App.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateResturantForm, updateRestaurantForm, SearchForm, ReviewForm, FavoriteListForm, MenuForm, MenuItemForm
# importing models
from App.models import User, Address, Label, MenuItem,FavoriteList, Menu, Restaurant, Review, Restaurant_Label,Restaurant_FavoriteList
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

#Utility Functions
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
#----------------------------------------------------------
@app.route("/")
@app.route("/home")
def home():
	form = SearchForm()
	if form.validate_on_submit():
		searchString = form.searchString.data
		restaurants = Restaurant.query.all()
		#TODO: implement the search algorithm here
	return render_template("home.html", title = 'Home', form = form)

@app.route("/about")
def about():
	return render_template('about.html', title='About')

# User Management Routes
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
	return render_template('register.html', title='Register',form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		global user
		global next_page
		user = User.query.filter_by(email=form.email.data).first()
		print("DEBUG")
		#print(user2.type)
		#print(form.type.data)
		#print(user.type)
		#print(form.type.data)
		if user.type =='RestaurantOwner' and form.type.data =='RestaurantOwner' :
			print(user.type)
			print(form.type.data)
			#user = User.query.filter_by(email=form.email.data).first()
			if user and bcrypt.check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('viewRestaurantOwner', userId = user.id))
		if user.type =='Customer' and form.type.data =='Customer'  :
			print(user.type)
			print(form.type.data)
			#user = User.query.filter_by(email=form.email.data).first()
			if user and bcrypt.check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check Email or Password and Account Type', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/viewRestaurantOwner/<userId>", methods=['GET', 'POST'])
@login_required
def viewRestaurantOwner(userId):
	restaurant = Restaurant.query.filter_by(user_id = userId).first()
	if restaurant:
		return render_template('viewRestaurantOwner.html', title='Restaurant', restaurant= restaurant)

	else:
		flash('You Do Not Have a Restaurant Yet, Please Create Restaurant First', 'danger')
		return redirect(url_for('createRestaurant',userId = userId))

#return render_template('creatRestaurant.html', title=' Create Restaurant', userId= userId)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		#if form.picture.data:
		#	picture_file = save_picture(form.picture.data)
		#current_user.photo = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('account.html', title='Account', form=form)

#----------------------------------------------------------

#Restaurant CRUD
@app.route("/createRestaurant/<userId>", methods=['GET', 'POST'])
@login_required
def createRestaurant(userId):
	form = CreateResturantForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture_restaurant(form.picture.data)
		address = Address(streetAddress = form.streetAddress.data, unitNumber = form.unitNumber.data, city = form.city.data, state = form.state.data, zipCode = form.zipCode.data, country = form.country.data)
		db.session.add(address)
		db.session.commit()
		pictureFile = save_picture_restaurant(form.picture.data)
		restaurant = Restaurant(name=form.name.data, phoneNumber = form.phoneNumber.data,description = form.description.data, picture = pictureFile, address_id = address.id, user_id = userId)
		db.session.add(restaurant)
		db.session.commit()
		flash('Your restaurant has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('createRestaurant.html', title='Create Restaurant',form=form)

@app.route("/updateRestaurant/<restaurantId>", methods=['GET', 'POST'])
@login_required
def updateRestaurant(restaurantId):
	restaurant = Restaurant.query.filter_by(id=restaurantId).first()
	form = updateRestaurantForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			restaurant.picture = picture_file
		restaurant.name = form.name.data
		restaurant.phoneNumber = form.phoneNumber.data
		#current_user.type = form.type.data
		restaurant.description = form.description.data
		#current_user.address = form.address.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('home'))
	elif request.method == 'GET':
		form.name.data = restaurant.name
		form.phoneNumber.data = restaurant.phoneNumber
		form.description.data= restaurant.description
	return render_template('updateRestaurant.html', title='Account',restaurant = restaurant, form=form)



@app.route("/viewRestaurant/<restaurantId>", methods=['GET', 'POST'])
#TODO: @login_required
def viewRestaurant(restaurantId):
	restaurant = Restaurant.query.get_or_404(restaurantId)
	return render_template('viewRestaurant.html', title='Restaurant', restaurant= restaurant)

# Review CRUD
@app.route("/addReview")
#@login_required
def addReview():
	form = ReviewForm()
	#if form.validate_on_submit():
	return render_template('review.html', title='Review', form=form)
