#Configuration File

userTypes = [('Customer','Customer'), ('RestaurantOwner','RestaurantOwner')]

ratingChoices = [('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5')]

# Database connection parameters
connection = {
	'host' : 'dbmysql.cpbuyejbc4kx.us-west-2.rds.amazonaws.com',
	'database' : 'FoodDB',
	'user' : 'mustafa',
	'password' : 'mustafa_DBMySQL'
}

# states list from https://www.census.gov/geo/maps-data/data/tiger-geodatabases.html
USStates = [
'Alabama',
'Alaska',
'Arizona',
'Arkansas',
'California',
'Colorado',
'Connecticut',
'Delaware',
'District of Columbia',
'Florida',
'Georgia',
'Hawaii',
'Idaho',
'Illinois',
'Indiana',
'Iowa',
'Kansas',
'Kentucky',
'Louisiana',
'Maine',
'Maryland',
'Massachusetts',
'Michigan',
'Minnesota',
'Mississippi',
'Missouri',
'Montana',
'Nebraska',
'Nevada',
'New Hampshire',
'New Jersey',
'New Mexico',
'New York',
'North Carolina',
'North Dakota',
'Ohio',
'Oklahoma',
'Oregon',
'Pennsylvania',
'Puerto Rico',
'Rhode Island',
'South Carolina',
'South Dakota',
'Tennessee',
'Texas',
'Utah',
'Vermont',
'Virginia',
'Washington',
'West Virginia',
'Wisconsin',
'Wyoming']