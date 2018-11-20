from flask import Flask, render_template, request, redirect, url_for,session,flash
from flaskext.mysql import MySQL
from functools import wraps
import mysql.connector
app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'project2'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT']=33306
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'

mysql.init_app(app)
mysql = MySQL(app)
conn = mysql.connect()
cur = conn.cursor()
#################################################### Session ############################################
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('unauthorized, please login and proceed', 'danger')
            return redirect(url_for('index'))
    return wrap

################################################## MAIN  ################################################
@app.route('/', methods = ['GET' ,'POST'])
def index():
    return render_template('Main.html')

#################################################### STUDENT #############################################
@app.route('/studentlogin/', methods = ['GET', 'POST'])
def studentlogin():
    if request.method == 'POST':
        user_details = request.form
        password = str(user_details['pass'])
        id = str(user_details['id'])
        try:
            cur.execute("select roll_no from student where roll_no =%s;", id)
            mroll = cur.fetchone()
            mroll = str(mroll[0])
            cur.execute("select pass from student where roll_no =%s;", id)
            pas = cur.fetchone()
            pas = str(pas[0])
            cur.execute("select roll_no, sname, email, phno, cetranking from student where  roll_no = %s;", id)
            # data=cur.fetchall()
            if id == mroll and password == pas:
                session['logged_in'] = True
                session['username'] = id
                flash('you are logged in', 'success')
                return redirect(url_for('search', roll=mroll, branch='all', loc='all'))
            else:
                return 'invalid password'
        except:
            msg='invalid user_id'
            return render_template('studentlogin.html',msg=msg)
    msg='Login with your user_id and Password'
    return render_template('studentlogin.html',mesg=msg)

########################################################### myHome #################################################
@app.route('/myhome/<roll>')
def myhome(roll):
    cur.execute('select roll_no,sname,c.phno,cetranking,bname,cname,c.email,loc from student s,college c where roll_no=%s and c.cid=s.cid',roll)
    data=cur.fetchall()
    return render_template('home.html',data=data)

############################################################## student forgot #######################################
@app.route('/forgot/<id>',methods=['GET','POST'])
def forgot(id):
    try:
            if request.method == 'POST':

                forgot = request.form
                ans = forgot['ans']
                cur.execute("select forgot from student where roll_no=%s",id)
                ans1 = cur.fetchone()
                ans1 = ans1[0]
                if ans == ans1:
                    cur.execute("select pass from student where roll_no=%s",id)
                    passs=cur.fetchone()
                    passs=passs[0]
                    password = 'your password is '+ passs
                    flash(password)
                    return redirect(url_for('studentlogin'))
            cur.execute("select forgot_que from student where roll_no=%s", id)
            que = cur.fetchone()
            return render_template('forgot.html',que=que)
    except:
        return 'no roll number exists'
###################################################### Roahn ###############################################3

@app.route('/rohan/',methods=['GET','POST'])

def rohan():
    if request.method == 'POST':
        roh = request.form
        id = roh['rol']
        return redirect(url_for('forgot',id=id))
    return render_template('rohan.html')

###################################################### STUDENT_SIGNUP #########################################
@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
        if request.method == 'POST':
            # fetch the from data
            user_details = request.form
            roll = (user_details['roll'])
            name = str(user_details['name'])
            pas = str(user_details['pas'])
            email = str(user_details['email'])
            phno = int(user_details['ph'])
            cranking = int(user_details['cet'])
            ans=str(user_details['ans'])
            que=str(user_details['que'])
            cur.execute("select roll_no , sname, rank from cet_rank where roll_no=%s", roll)
            data = cur.fetchall()
            rolll = (data[0][0])
            sname = data[0][1]
            rank = data[0][2]
            try:
                if roll == rolll and rank == cranking and sname == name:
                    session['logged_in'] = True
                    session['username'] = rolll
                    flash('sign up succussfull', 'success')
                    cur.execute(
                        "insert into student ( roll_no , sname, pass , email, phno ,cetranking,forgot, forgot_que) values (%s, %s, %s, %s, %s, %s,%s,%s);",
                        (roll, name, pas, email, phno, cranking, ans, que))
                    conn.commit()
                    return redirect(url_for('search', roll=rolll, branch='all', loc='all'))
                else:
                    return 'invalid password'
            except:
                return 'invalid information'
        return render_template('signup.html')

###################################################### SEARCH ###################################################
@app.route('/search/<roll>/<branch>/<loc>',methods=['GET','POST'])
@is_logged_in
def search(roll, branch, loc):
    if request.method == 'POST':
        # fetch the from data
        search_details = request.form
        loc = str(search_details['loct'])
        branch = str(search_details['clg'])
        cur.execute("select cetranking from student where roll_no=%s ", roll)
        ro = cur.fetchone()
        ro = ro[0]
        if branch == 'all'and loc == 'all':
            cur.execute("select c.cid,c.cname,c.loc,b.bname,b.seats,b.fees, b.cutoff from college c , branch b where c.cid=b.cid and b.cutoff>%s",ro)
        elif branch == 'all':
            cur.execute("select c.cid,c.cname,c.loc,b.bname,b.seats,b.fees,b.cutoff from college c , branch b where c.cid=b.cid and b.cutoff>%s and loc=%s",( ro, loc))
        elif loc == 'all':
            cur.execute("select c.cid,c.cname,c.loc,b.bname,b.seats,b.fees ,b.cutoff from college c , branch b where c.cid=b.cid and b.cutoff>%s and bname=%s", (ro, branch))
        else:
            cur.execute("select c.cid,c.cname,c.loc,b.bname,b.seats,b.fees ,b.cutoff from college c , branch b where c.cid=b.cid and b.cutoff>%s and bname=%s and loc=%s", (ro, branch, loc))
        res = cur.fetchall()
        return render_template('search.html', roll=roll, loc=loc, branch=branch, res=res)
    cur.execute("select cetranking from student where roll_no=%s ", roll)
    ro = cur.fetchone()
    ro = ro[0]
    cur.execute("select c.cid,c.cname,c.loc,b.bname,b.seats,b.fees,b.cutoff from college c , branch b where c.cid=b.cid and b.cutoff>%s",ro)
    res = cur.fetchall()
    return render_template('search.html', roll=roll, loc=loc, branch=branch,res=res)

######################################################### Studentupdate ############################################
@app.route('/studentupdate/<roll>', methods=['GET','POST'])
@is_logged_in
def studentupdate(roll):
    if request.method == 'POST':
        stdup = request.form
        new_pass = stdup['pass']
        new_email = stdup['email']
        new_phone = stdup['phno']
        cur.execute("update student set email=%s where roll_no=%s",(new_email, roll))
        conn.commit()
        cur.execute("update student set phno=%s where roll_no=%s",(new_phone, roll))
        conn.commit()
        cur.execute("update student set pass=%s where roll_no=%s", (new_pass, roll))
        conn.commit()
        mes='update done'
        flash(mes)
        return redirect(url_for('studentlogin'))
    cur.execute("select  email, pass, phno from student where  roll_no = %s;", roll)
    data=cur.fetchall()
    return render_template('studentupdate.html', data=data)

##################################################### Join #########################################
@app.route('/join/<roll>/<cid>/<bname>')
@is_logged_in
def join(roll, cid, bname):
    cur.execute("select roll_no from student where cid is not null and roll_no=%s", roll)
    new_roll = cur.fetchone()
    if new_roll:
        msg = 'already joined'
        return roll+" " + msg

    else:
        cur.execute("update student set cid=%s where roll_no=%s;", (cid, roll))
        conn.commit()
        cur.execute("update student set bname=%s where roll_no=%s;", (bname, roll))
        conn.commit()
        return  " The "+ roll+" has  joined to " +cid+" and  "+ bname


############################################# Student delete ##############################################
@app.route('/studentdelete/<roll>')
def studentdelete(roll):
    cur.execute("delete from student where roll_no=%s", roll)
    conn.commit()
    mesg='is deleted'
    return roll+" "+mesg

############################################## COLLEGE Login####################################################
@app.route('/college/', methods = ['GET' , 'POST'])
def college():
    if request.method == 'POST':
        userdetails = request.form
        Password = str(userdetails['pass'])
        id = int(userdetails['id'])
        cur.execute("select cid from college where cid =%s;", id)
        mroll = cur.fetchone()
        mroll = int(mroll[0])
        cur.execute("select pass from college where cid =%s;", id)
        pas = cur.fetchone()
        pas = str(pas[0])
        try:
            if id == mroll and Password == pas:
                session['logged_in'] = True
                session['username'] = id
                flash('you are logged in', 'success')
                return redirect(url_for('collegemain',id=id))
            else:
                return 'invalid password'
        except:
            return 'invalid information'
    return render_template('college.html')
#######################################################College Main##############################################
@app.route('/collegemain/<id>',methods=['GET','POST'])
@is_logged_in
def collegemain(id):
    cur.execute('select cname from college where cid=%s',id)
    cname=cur.fetchone()
    cname=cname[0]
    cur.execute("select * from student where cid = %s; ", id)
    data = cur.fetchall()
    return render_template('join.html',data=data,id=id,cname=cname)

######################################################## College Forget#############################################
@app.route('/collegeforgot/<i>',methods=['GET','POST'])
def collegeforgot(i):
    if request.method == 'POST':
        got = request.form
        ans = got['ans']
        try:
            cur.execute("select forgot from college where cid=%s", i)
            ans1 = cur.fetchone()
            ans1 = ans1[0]
            if ans == ans1:
                cur.execute("select pass from college where cid=%s", i)
                pas = cur.fetchone()
                pas = pas[0]
                mesg = "your password is " + pas
                flash(mesg)
                return redirect(url_for('college'))
            else:
                return 'invalid answer'
        except:
            return "there is no college, please put the correct college id"
    cur.execute("select for_que from college where cid=%s", i)
    que = cur.fetchone()
    return render_template('colforget.html',que=que)

###################################################### college ###############################################3

@app.route('/colfor/',methods=['GET','POST'])
def colfor():
    if request.method == 'POST':
        coll = request.form
        i = coll['rol']
        return redirect(url_for('collegeforgot',i=i))
    return render_template('col.html')



########################################################College INFO #######################################
@app.route('/collegeinfo/<id>')
@is_logged_in
def collegeinfo(id):
    cur.execute("select * from college where cid=%s", id)
    data=cur.fetchall()
    return render_template('clginfo.html', data=data)

################################################## CollegeUpdate ############################################
@app.route('/collegeupdate/<id>',methods=['GET','POST'])
@is_logged_in
def collegeupdate(id):
    if request.method == 'POST':
        cupdate = request.form
        new_Phno = cupdate['phno']
        new_email = cupdate['email']
        new_pass = cupdate['pass']
        cur.execute("update college set email=%s where cid=%s",(new_email, id))
        conn.commit()
        cur.execute("update college set phno=%s where cid=%s", (new_Phno, id))
        conn.commit()
        cur.execute("update college set pass=%s where cid=%s", (new_pass, id))
        conn.commit()
        mesg = " update done "
        flash(mesg)
        return redirect(url_for('college'))
    cur.execute("select * from college where cid=%s", id)
    data=cur.fetchall()
    return render_template('collegeupdate.html', data=data)

##################################################### BranchUpdate #########################################
@app.route('/branchupdate/<id>',methods=['GET','POST'])
@is_logged_in
def branchupdate(id):
    if request.method == 'POST':
        bupdate = request.form
        bname = bupdate['bname']
        new_seats = bupdate['seats']
        new_cutoff = bupdate['cutoff']
        new_fees = bupdate['fees']
        cur.execute("update branch set seats=%s where cid=%s and bname=%s ", (new_seats, id, bname))
        conn.commit()
        cur.execute("update branch set cutoff=%s where cid=%s and bname=%s", (new_cutoff, id, bname))
        conn.commit()
        cur.execute("update branch set fees=%s where cid=%s and bname=%s", (new_fees, id, bname))
        conn.commit()
        msg='update done'
        flash(msg)
        return redirect(url_for('branchupdate', id=id))
    cur.execute("select * from branch where cid=%s", id)
    data=cur.fetchall()
    cur.execute('select cname from college where cid=%s', id)
    cname = cur.fetchone()
    cname = cname[0]
    return render_template('branchupdate.html', data=data,id=id,cname=cname)


########################################################### Add Branch ##############################################
@app.route('/addbranch/<id>',methods=['GET','POST'])
@is_logged_in
def addbranch(id):
    if request.method=='POST':
        addbranch=request.form
        cid=addbranch['id']
        bname=addbranch['bname']
        seats=addbranch['seats']
        cutoff=addbranch['cutoff']
        fees=addbranch['fees']
        cur.execute("insert into branch (cid,bname,seats,cutoff,fees) values (%s,%s,%s,%s,%s)",(cid,bname,seats,cutoff,fees))
        conn.commit()
        return redirect(url_for('branchupdate', id=id))
    return render_template('addbranch.html', id=id)

########################################################### ADMIN ##################################################
@app.route('/admin/', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user_details = request.form
        password = str(user_details['pass'])
        id = int(user_details['id'])
        cur.execute("select aid from admin where aid =%s;", id)
        mroll = cur.fetchone()
        mroll = int(mroll[0])
        cur.execute("select pass from admin where aid =%s;", id)
        pas = cur.fetchone()
        pas = str(pas[0])
        if id == mroll and password == pas:
            session['logged_in'] = True
            session['username'] = id
            flash('you are logged in', 'success')
            cur.execute("select aname from admin where aid =%s;", id)
            aname = cur.fetchone()
            aname = str(aname[0])
            return render_template('adminall.html', aname=aname)
        else:
            return 'invalid username or password'

    return render_template('admin.html')

########################################### Admin Forgot #########################################
@app.route('/adminforgot/',methods=['POST','GET'])
def adminforgot():
    if request.method == 'POST':
        adminfor = request.form
        id = adminfor['id']
        return redirect(url_for('adforget', id=id))
    return render_template('mareu.html')

########################################### Admin answwer #########################################
@app.route('/adforget/<id>',methods=['GET','POST'])
def adforget(id):
    if request.method == 'POST':
        got = request.form
        ans = got['ans']
        try:
            cur.execute("select answer from admin where aid=%s", id)
            ans1 = cur.fetchone()
            ans1 = str(ans1[0])
            if ans == ans1:
                cur.execute("select pass from admin where aid=%s", id)
                pas = cur.fetchone()
                pas = pas[0]
                mesg = "your password is " + pas
                flash(mesg)
                return redirect(url_for('admin'))
            else:
                return 'invalid answer'
        except:
            return "there is no Admin, please put the correct Admin id"
    cur.execute("select question from admin where aid=%s", id)
    que = cur.fetchone()
    que=que[0]
    return render_template('sikttu.html',que=que)

########################################### Admin can search student info #########################################
@app.route('/adminstudent/<id>',methods=['GET','POST'])
@is_logged_in
def adminstudent(id):
    if request.method == 'POST':
        student_login = request.form
        rolll = student_login['rol']
        if rolll == 'all':
            cur.execute("select * from student")
            data = cur.fetchall()
        else:
            cur.execute("select * from student where roll_no=%s", rolll)
            data = cur.fetchall()
        return render_template('adminstudent.html', roll=rolll, data=data)
    cur.execute("select * from student")
    data = cur.fetchall()
    return render_template('adminstudent.html', id=id, data=data)

################################################## Admin add college ################################################
@app.route('/addcollege/',methods=['GET','POST'])
@is_logged_in
def addcollege():
    if request.method=='POST':
        addcol=request.form
        cid=int(addcol['cid'])
        cname=str(addcol['cname'])
        passs=str(addcol['pas'])
        loc=str(addcol['loc'])
        phno=str(addcol['phno'])
        email=str(addcol['email'])
        forg=str(addcol['ans'])
        for_que=str(addcol['que'])
        cur.execute("insert into college  (cid,cname,pass,loc,phno,email,forgot,for_que) values (%s,%s,%s,%s,%s,%s,%s,%s);",(cid,cname,passs,loc,phno,email,forg,for_que))
        conn.commit()
        mesg="college added"
        flash(mesg)
        return redirect(url_for('college'))
    return render_template('collegeadd.html')

########################################################## View ##############################################
@app.route('/view/<id>')
def view(id):
    return redirect(url_for('collegemain',id=id))

################################################## Admin can search college info ######################################
@app.route('/admincollege/<id>',methods=['GET','POST'])
@is_logged_in
def admincollege(id):
    if request.method == "POST":
        coll = request.form
        cid = coll['col']
        if cid == 'all':
            cur.execute("select * from college ")
            data = cur.fetchall()
        else:
            cur.execute("select * from college where cid=%s", cid)
            data = cur.fetchall()
        return render_template('admincollege.html', cid=cid, data=data)
    cur.execute("select * from college")
    data=cur.fetchall()
    return render_template('admincollege.html', id=id, data=data)

##################################################### Admin delete college #######################################
@app.route('/collegedelete/<id>')
def collegedelete(id):
    cur.execute("delete from college where cid= %s", id)
    conn.commit()
    mesg = 'is deleted'
    return " the college "+id+" "+mesg

########################################################### Admin add student ####################################
@app.route('/adminaddstudent/',methods=['GET','POST'])
@is_logged_in
def adminaddstudent():
    if request.method=='POST':
        adminstd=request.form
        roll=adminstd['rol']
        name=adminstd['name']
        rank=adminstd['rank']
        if roll:
         cur.execute("insert into cet_rank (roll_no,sname,rank) values (%s,%s,%s)",(roll,name,rank))
         conn.commit()
        return redirect(url_for('admincet'))
    return render_template('adminstd.html')

######################################################### Admin cet #########################################
@app.route('/admincet/',methods=['GET','POST'])
@is_logged_in
def admincet():
    if request.method == 'POST':
        cet = request.form
        cet = cet['cet']
        cur.execute('select roll_no from cet_rank where roll_no=%s',cet)
        ect = cur.fetchone()
        ect = ect[0]
        if cet == ect:
            cur.execute("select * from cet_rank where roll_no=%s",cet)
            data = cur.fetchall()
        else:
            cur.execute("select * from cet_rank")
            data = cur.fetchall()
        return render_template('admincet.html',data=data)
    cur.execute("select * from cet_rank")
    data = cur.fetchall()
    return render_template("admincet.html", data=data)

######################################################### Admin cet Delete ##################################
@app.route('/admincetdelete/<id>')
@is_logged_in
def admincetdelete(id):
    cur.execute("delete from cet_rank where roll_no= %s", id)

    conn.commit()
    mesg = 'is deleted'
    return id + " " + mesg

#######################################################  Logout #####################################
@app.route('/logout/')
def logout():
    session.clear()
    flash('you are now logged out')
    return render_template('Main.html')

########################################### MAIN_FUNCTION #################################################
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000
    app.run(HOST, PORT, debug='true')