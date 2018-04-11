import pymysql
from models import db

conn = pymysql.connect(host='localhost', user='root', password='123')
conn.cursor().execute('CREATE DATABASE IF NOT EXISTS inventory')