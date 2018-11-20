from flask import Flask, render_template, request,redirect,url_for
from flaskext.mysql import MySQL
import mysql.connector
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'project2'
app.config['MYSQL_DATABASE_HOST']='3306'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app)
conn = mysql.connect()
cur = conn.cursor()

@app.route('/')
def index():
    return "succcess"
if __name__ == '__main__':

    import os

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000
    app.run(HOST, PORT,debug='true')