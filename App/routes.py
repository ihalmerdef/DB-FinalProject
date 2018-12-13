import os
import secrets
import mysql.connector
from mysql.connector import Error
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from App import app, db, bcrypt
#importing forms
from App.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddResturantForm, updateRestaurantForm, SearchForm, ReviewForm, FavoriteListForm, MenuForm, MenuItemForm
# importing models
from App.models import User, Address, Label, MenuItem, FavoriteList, Menu, Restaurant, Review, Restaurant_Label, Restaurant_FavoriteList
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from App.config import connection

#Utility Functions
def save_picture_restaurant(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/restaurant_pics', picture_fn)
	output_size = (300, 300)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn

def buildSearchQuery(searchString):
	listOfWords = searchString.split(" ")
	searchQuery = ".*" + listOfWords[0]
	for i in range(1, len(listOfWords)):
		searchQuery = searchQuery + '.*' + listOfWords[i]
	searchQuery = searchQuery + '.*'
	return searchQuery
#----------------------------------------------------------
@app.route("/", methods = ['GET', 'POST'])
@app.route("/home", methods = ['GET', 'POST'])
def home():
	searchQuery = ""
	form = SearchForm()
	restaurantsNearBy = None
	if form.validate_on_submit():
		searchString = form.searchString.data
		#tokenization
		searchQuery = buildSearchQuery(searchString)
		try:
			conn = mysql.connector.connect(host = connection['host'],database = connection['database'], user = connection['user'], password = connection['password'])
			if conn.is_connected():
				cursor = conn.cursor(dictionary = True)
				cursor.execute("SELECT * FROM `restaurant` WHERE name RLIKE '" + searchQuery + "' OR description RLIKE '" + searchQuery + "'")
				searchResults = cursor.fetchall()
				return render_template("searchResults.html", title = "Search Result", searchResults = searchResults)
		except Error as e:
			print(e)
		finally:
			conn.close()
	if current_user.is_authenticated:	
		userZipCode = Address.query.get(current_user.address_id).zipCode
		restaurantsNearBy = Restaurant.query.join(Address, Restaurant.address_id == Address.id).add_columns(Restaurant.id, Restaurant.name, Restaurant.description, Restaurant.picture, Restaurant.user_id, Address.zipCode).filter(Address.zipCode == userZipCode)
	return render_template("home.html", title = "Home", form = form, restaurantsNearBy = restaurantsNearBy)

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
		user = User(firstName = form.firstName.data, lastName = form.lastName.data,  username = form.username.data, email = form.email.data, phoneNumber = form.phoneNumber.data, password = hashed_password,address_id = address.id,  type = form.userType.data)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title = 'Register',form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			nextPage = request.args.get('next')
			return redirect(nextPage) if nextPage else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.firstName = form.firstName.data
		current_user.lastName = form.lastName.data
		current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.phoneNumber = form.phoneNumber.data
		# updating the user's address
		address = Address.query.get((int)(current_user.address_id))
		address.streetAddress = form.streetAddress.data
		address.unitNumber = form.unitNumber.data
		address.city = form.city.data
		address.state = form.state.data
		address.zipCode = form.zipCode.data
		address.country = form.country.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		# populating the form fields
		form.firstName.data = current_user.firstName
		form.lastName.data = current_user.lastName
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.phoneNumber.data = current_user.phoneNumber
		address = Address.query.get((int)(current_user.address_id))
		form.streetAddress.data = address.streetAddress
		form.unitNumber.data = address.unitNumber
		form.city.data = address.city
		form.state.data = address.state
		form.zipCode.data = address.zipCode
		form.country.data = address.country
	return render_template('account.html', title = 'Account', form = form)

@app.route('/account/delete', methods = ['GET', 'POST'])
def deleteAccount():
	userId = request.args.get('userId')
	user = User.query.get((int)(userId))
	db.session.delete(user)
	db.session.commit()
	flash('You account has been delete', 'success')
	return redirect(url_for('home'))
#----------------------------------------------------------

#Restaurant CRUD

@app.route("/restaurant/view/", methods = ['GET', 'POST'])
def viewRestaurant():
	restaurantId = request.args.get('restaurantId')
	restaurant = None
	reviews = None
	reviewStats  = None
	try:
		conn = mysql.connector.connect(host = connection['host'],database = connection['database'], user = connection['user'], password = connection['password'])
		if conn.is_connected():
			cursor = conn.cursor(dictionary = True)
			cursor.execute("SELECT r.id as restaurantId, r.name as restaurantName, r.description as restaurantDescription, r.phoneNumber as restaurantPhoneNumber, r.picture as restaurantPicture, r.address_id as restaurantAddressId, r.user_id as restaurantUserId, a.id as addressId, a.streetAddress as addressStreetAddress, a.city as addressCity, a.state as addressState, a.zipCode as addressZipCode, a.country as addressCountry FROM `restaurant` as r JOIN address as a ON r.address_id = a.id WHERE r.id = '" + restaurantId + "'")
			restaurant = cursor.fetchone()
			print(restaurant)
			reviews = Review.query.filter(Review.restaurant_id == restaurantId).all()
			cursor.execute("SELECT AVG(rating) as averageRating, COUNT(id) as reviewCount FROM `review` WHERE restaurant_id = '" + restaurantId + "'")
			reviewStats = cursor.fetchone()
			if(reviewStats['averageRating']):
				reviewStats = {'averageRating': format(reviewStats['averageRating'], '.2f'), 'reviewCount':reviewStats['reviewCount']}
	except Error as e:
		print(e)
	finally:
		conn.close()
	print(restaurant)
	return render_template('viewRestaurant.html', title = 'Restaurant', restaurant= restaurant, reviews = reviews, reviewStats = reviewStats)


@app.route("/ownRestaurant/view", methods = ['GET', 'POST'])
@login_required
def viewRestaurantOwner():
	#using the same form as addRestaurant form to allow viewing and editing at the same time
	form = AddResturantForm()
	userId = request.args.get('userId')
	restaurant = Restaurant.query.join(Address, Restaurant.address_id == Address.id).add_columns(Restaurant.id, Restaurant.name, Restaurant.description, Restaurant.phoneNumber, Restaurant.picture, Restaurant.user_id, Restaurant.address_id, Address.streetAddress, Address.city, Address.state, Address.zipCode, Address.country).filter(Restaurant.user_id == userId).first()
	if (restaurant):
		reviews = Review.query.filter_by(restaurant_id = restaurant.id).all()
		restaurant_label = Restaurant_Label.query.join(Label, Restaurant_Label.label_id == Label.id).add_columns(Restaurant_Label.restaurant_id, Label.description).filter(Restaurant_Label.restaurant_id == restaurant.id).all()
		form.name.data = restaurant.name
		form.description.data = restaurant.description
		
		#form.labels.data = restaurant_label.description
		form.phoneNumber.data = restaurant.phoneNumber
		form.streetAddress.data = restaurant.streetAddress
		#form.unitNumber.data = restaurant.unitNumber
		form.city.data = restaurant.city
		form.state.data = restaurant.state
		form.zipCode.data = restaurant.zipCode
		form.country.data = restaurant.country
	
		return render_template('viewRestaurantOwner.html', title = 'view restaurant', form = form, restaurant = restaurant)
	else:
		flash('You do not have a restaurant yet. please create restaurant', 'danger')
		return redirect(url_for('addRestaurant', userId=current_user.id))

@app.route("/restaurant/add/", methods = ['GET', 'POST'])
@login_required
def addRestaurant():
	form = AddResturantForm()
	userId = request.args.get('userId')
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture_restaurant(form.picture.data)
		address = Address(streetAddress = form.streetAddress.data, unitNumber = form.unitNumber.data, city = form.city.data, state = form.state.data, zipCode = form.zipCode.data, country = form.country.data)
		db.session.add(address)
		db.session.commit()
		pictureFile = save_picture_restaurant(form.picture.data)
		restaurant = Restaurant(name = form.name.data, phoneNumber = form.phoneNumber.data,description = form.description.data, picture = pictureFile, address_id = address.id, user_id = userId)
		db.session.add(restaurant)
		db.session.commit()
		label = Label(description = form.label.data)
		for x in label.description:
			restaurant_label = Restaurant_Label(restaurant_id = restaurant.id, label_id = x)
			db.session.add(restaurant_label)
			db.session.commit()
		flash('Your restaurant has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('createRestaurant.html', title = 'Create Restaurant',form = form)

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

#Menu CRUD
@app.route("/menu/add", methods=['GET','POST'])
def addMenu():
	form = MenuForm()
	restaurantId = request.args.get('restaurantId')
	if form.validate_on_submit():
		menu = Menu(restaurant_id = restaurantId, name = form.menuName.data)
		db.session.add(menu)
		db.session.commit()
		flash('Your menu has been created! You are now able to add to it', 'success')
		return redirect(url_for('home'))
	return render_template('menu.html', title='Menu', form=form)

@app.route("/menu/view/all", methods = ['GET', 'POST'])
@login_required
def viewMenus():
		restaurantId = request.args.get('restaurantId')
		menus = Menu.query.filter_by(restaurant_id = restaurantId).all()
		#menus = Menu.query.join(MenuItem, MenuItem.menu_id == Menu.id).add_columns(Menu.id.label('menuId'), Menu.name.label('menuName'), Menu.restaurant_id, MenuItem.id.label('menuItemId'), MenuItem.name.label('menuItemName'), MenuItem.description, MenuItem.price, MenuItem.picture, MenuItem.menu_id.label('menuItemMenuId') ).filter(Menu.id == menuId).all()
		return render_template('viewMenus.html', title = 'View Menus', menus = menus)

@app.route("/deleteMenu", methods = ['GET'])
def deleteMenu():
	menuId = request.args.get('menuId')
	menu = Menu.query.get((int)(menuId))
#----------------------------------------------------------

# Review CRUD
@app.route("/review/add", methods = ['GET', 'POST'])
def addReview():
	form = ReviewForm()
	if form.validate_on_submit():
		userId = request.args.get('userId')
		restaurantId = request.args.get('restaurantId')
		now = datetime.utcnow()
		review = Review(rating = form.rating.data, comment = form.comment.data, date = now, restaurant_id = restaurantId, user_id = userId)
		db.session.add(review)
		db.session.commit()
		flash('Your review has been created! Thanks', 'success')
		return redirect(url_for('home'))
	return render_template('review.html', title='review', form = form)

@app.route("/review/update", methods = ['GET', 'POST'])
def updateReview():
	form = ReviewForm()
	# change the submit field value
	form.submit.label.text = 'Update'
	reviewId = request.args.get('reviewId')
	review = Review.query.get((int)(reviewId))
	if form.validate_on_submit():
		now = datetime.utcnow()
		review.rating = form.rating.data
		review.comment = form.comment.data
		review.date = now
		db.session.commit()
		flash('Your review has been updated!', 'success')
		return redirect(url_for('home'))
	elif request.method == 'GET':
		form.rating.default = review.rating
		form.comment.data = review.comment
	return render_template('review.html', title = 'review', form = form)

@app.route("/review/delete", methods = ['GET'])
def deleteReview():
	# reading the query parameter from the query string (deleteReview?reviewId=xyx)
	reviewId = request.args.get('reviewId')
	print("DEBUG reviewId = " + reviewId)
	review = Review.query.get((int)(reviewId))
	print('DEBUG: review:')
	print(rieview)
	if review:
		db.session.delete(review)
		db.session.commit()
		flash('Your review has been delete!', 'success')
	return redirect(url_for('home'))
#---------------------------------------------------------

#FavoriteList CRUD
@app.route("/favoriteList/viewAll", methods = ['GET', 'POST'])
def favoriteList():
	form = FavoriteListForm()
	userId = request.args.get('userId')
	favoriteLists = FavoriteList.query.filter_by(user_id = userId).all()
	print(favoriteLists)
	if form.validate_on_submit():
		favoriteList = FavoriteList(name = form.name.data, user_id = current_user.id)
		db.session.add(favoriteList)
		db.session.commit()
		flash('Your list has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('favoriteLists.html', title='Favorite List', form = form, favoriteLists = favoriteLists)

@app.route("/favoriteList/view", methods = ['GET', 'POST'])
def viewFavoriteList():
	favoriteListId = request.args.get('favoriteListId')
	favoriteList = FavoriteList.query.get((int)(favoriteListId))
	try:
		conn = mysql.connector.connect(host = connection['host'],database = connection['database'], user = connection['user'], password = connection['password'])
		if conn.is_connected():
			cursor = conn.cursor(dictionary = True)
			cursor.execute("SELECT * FROM restaurant_favoriteList JOIN restaurant ON restaurant_favoriteList.restaurant_id = restaurant.id AND restaurant_favoriteList.favoriteList_id = '" + favoriteListId + "'")
			restaurants = cursor.fetchall()
	except Error as e:
		print(e)
	finally:
		conn.close()
	return render_template('favoriteList.html', title =' Favorite List', favoriteList = favoriteList, restaurants = restaurants)

@app.route("/favoriteList/delete", methods = ['GET', 'POST'])
def deleteFavoriteList():
	favoriteListId = request.args.get('favoriteListId')
	print('#DEBUG')
	print('inside deleteFavoriteList')
	print(favoriteListId)
	favoriteList = FavoriteList.query.get((int)(favoriteListId))
	db.session.delete(favoriteList)
	db.session.commit()
	flash('Your list has been deleted!', 'success')
	return redirect(url_for('favoriteList',userId=current_user.id ))
#---------------------------------------------------------
#MenuItem CRUD
@app.route("/menu/view/", methods = ['GET', 'POST'])
@login_required
def viewMenu():
	menuId = request.args.get('menuId')
	menuItems = MenuItem.query.filter_by(menu_id = menuId).all()
	return render_template('viewMenuItems.html', title = 'View Menu Items', menuItems = menuItems)

@app.route("/addMenuItem/<menuId>", methods=['GET','POST'])
def addMenuItem(menuId):
	form = MenuItemForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture_restaurant(form.picture.data)
		item = MenuItem(name=form.name.data, description=form.description.data, picture=picture_file,price=form.price.data,menu_id=menuId)
		db.session.add(item)
		db.session.commit()
		flash('Items has been created for your menu!', 'success')
	return render_template('addMenuItem.html', title = 'Add Item', form = form)

#---------------------------------------------------------

#FavoriteList CRUD
@app.route("/restaurant/favoriteList/add")
@login_required
def addRestaurantToFavoriteList():
	form = AddResturantToFavoriteListForm()
	restaurantId = request.args.get('restaurantId')
	favoriteListId = request.args.get('favoriteListId')
	restaurant_FavoriteList = Restaurant_FavoriteList(restaurant_id = restaurantId, favoriteList_id = FavoriteList_id)
	db.session.add(restaurant_FavoriteList)
	db.session.commit()
	return
#---------------------------------------------------------