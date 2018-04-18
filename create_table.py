import os
import pymysql
from app import db

try:
	print "Creating database tables"
	db.create_all()
except Exception as error:
	print 'Got an error: {}'.format(error)
	conn = pymysql.connect(host='localhost', user='root', password='')
	conn.cursor().execute('CREATE DATABASE IF NOT EXISTS inventory')
	conn.cursor().execute('CREATE DATABASE IF NOT EXISTS test_inventory')
	print "Creating database tables"
	db.create_all()
	