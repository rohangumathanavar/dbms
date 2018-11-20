from flask import Flask ,render_template , request
from flaskext.mysql import MySQL
import mysql.connector
app=Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'project2'
app.config['MYSQL_DATABASE_HOST'] = '3306'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql=MySQL(app)
conn=mysql.connect()
cur = conn.cursor()
cur.execute("select * from users;")
data = cur.fetchall()
print(data)
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # fetch the from data
       try:
           userdetails = request.form
           Name =userdetails['user']
           Password =userdetails['pass']
           ID=userdetails['id']
           conn = mysql.connect()
           cur = conn.cursor()
           cur.execute("insert into users (id,rame,sassword) values (%s,%s,%s )",(ID,Name,Password))

           """cur.execute("select rame from users where rame =%s;", Name)
           mroll = cur.fetchone()
           mroll = mroll[0]
           print(mroll)
           cur.execute("select sassword from users where rame =%s;", Name)
           passs = cur.fetchone()
           passs = passs[0]
           print(passs)

           if Name == mroll and Password == passs:
               
           else:
               return 'invalid username and password'"""
           conn.commit()
           conn.close()
           return 'success'
       except:
           return "invalid name or password "



if __name__=='__main__':

    import os

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '1222'))
    except ValueError:
        PORT = 1222
    app.run(HOST, PORT,debug='true')