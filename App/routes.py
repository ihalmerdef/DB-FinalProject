import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from App import app, db, bcrypt
from App.forms import RegistrationForm, LoginForm, UpdateAccountForm, creat_resturantForm, update_resturantForm
# importing models
from App.models import Address, Customer, Favorite_List, Label, MenuItem,Favorite_List, Menu, Restaurant, RestaurantOwner, Review, Restaurant_Label
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route("/")
#def index():
#	return render_template("index.html", title = 'Index')

@app.route("/home")
def home():
	return render_template("home.html", title = 'Home')


#@app.route("/upload", methods=['POST'])
#def upload():
#	file = request.files['inputFile']
#	newFile = Photos(data=file.read())
#	db.session.add(newFile)
#	db.session.commit()
#	flash('Your Image has been uploaded!', 'success')
#	return render_template('home.html', title='home')

#@app.route("/viewphoto", methods=['GET', 'POST'])
#def viewphoto():
#	Viewphoto= Photos.query.all()
#	return render_template('viewphoto.html', title='view_photo', Viewphoto= Viewphoto )



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
		user = Customer(firstName = form.firstName.data, lastName = form.lastName.data, username = form.username.data, email = form.email.data, password = hashed_password)
		address = Address(streetAddress = form.streetAddress.data, unitNumber = form.unitNumber.data, city = form.city.data, state = form.state.data, zipCode = form.zipCode.data, country = form.country.data)
		db.session.add(user)
		db.session.add(address)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('login'))
#picture_file= url_for('static', filename='profile_pics/' + resturant.photo)
	return render_template('register.html', title='Register',form=form)

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route("/creat_resturant", methods=['GET', 'POST'])
@login_required
def creat_resturant():
	form = creat_resturantForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
		resturant = Restaurant(name=form.name.data, phone_number=form.phone_number.data,description=form.description.data,picture=form.picture.data)
		db.session.add(resturant)
		db.session.commit()
		flash('Your resturant has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('creat_resturant.html', title='CreateResturant',form=form)

@app.route("/update_resturant", methods=['GET', 'POST'])
@login_required
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



@app.route("/view_resturant", methods=['GET', 'POST'])
@login_required
def view_resturant():
	ViewRestuants= Restaurant.query.all()
	return render_template('view_resturant.html', title='Account', ViewRestuants= ViewRestuants )



@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
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
	photo= url_for('static', filename='profile_pics/' + current_user.photo)
	return render_template('account.html', title='Account', photo=photo, form=form)
