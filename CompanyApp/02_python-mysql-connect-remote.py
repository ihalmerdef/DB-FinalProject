import mysql.connector
from mysql.connector import Error
 
 
def connect():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='dbmysql.cpbuyejbc4kx.us-west-2.rds.amazonaws.com',
                                       database='FoodDB',
                                       user='mustafa',
                                       password='mustafa_DBMySQL')
        if conn.is_connected():
            print('Connected to MySQL database')
 
    except Error as e:
        print(e)
 
    finally:
        conn.close()
 
 
if __name__ == '__main__':
    connect()

