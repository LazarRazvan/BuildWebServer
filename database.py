from influxdb import InfluxDBClient
import hashlib

def get_client(host_name, port_nr):
	"""
	Return a connection to database on a givem hostname
	and a port number
	"""
	return InfluxDBClient(host=host_name, port=port_nr)

def get_databse(databases, database_name):
	"""
	Search for a database
	"""
	res = [database['name'] for database in databases if database['name'] == database_name]
	if not res:
		return False
	return True

def add_user(username, password):
	"""
	This function add a user to database

	@username: Username
	@password: User password

	In addition to this, a custom uid is generated and added into the database.
	This will be used to identify an user.
	"""
	string = username + password
	uid = hashlib.md5(string.encode('utf-8'))
	print (uid)

def main():
	name = 'users'
	client = get_client('localhost', 8086)
	databases = client.get_list_database()
	if not get_databse(databases, name):
		client.create_databases(name)
	else:
		print ('Database is already created')

	# Switch to the user database
	client.switch_database(name)
	add_user('mihai', 'maria')

if __name__ == "__main__":
	main()