import os
import pymysql
from app import db

try:
	print "Creating database tables"
	db.create_all()
except Exception:
	conn = pymysql.connect(host='localhost', user='root', password='123')
	conn.cursor().execute('CREATE DATABASE IF NOT EXISTS dev')
	print "Creating database tables"
	db.create_all()