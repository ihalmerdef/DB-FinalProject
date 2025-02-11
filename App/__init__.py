from flask import Flask
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from mysql.connector import Error
from App.config import connection


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + connection['user'] + ':' + connection['password'] + '@' + connection['host'] + '/' + connection['database']

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from App import routes
from App import models
from App import config

models.db.create_all()

# def connect():
	# """ Connect to MySQL database """
	# try:
		# conn = mysql.connector.connect(host = host,database = database, user = user, password = password)
		# if conn.is_connected():
			# print('Connected to MySQL database via Mysql Connector')
	# except Error as e:
		# print(e)
	# finally:
		# conn.close()
# connect()
