from flask import Flask,render_template,redirect,url_for,request,flash,session
import mysql.connector
from cmail import sendmail
from otp import genotp
app=Flask(__name__)
#secret key
app.config['SECRET_KEY'] = "my super secret key that no one  is supposed to know"
mydb=mysql.connector.connect(host='localhost',user='root',password='system',db='nagu')
with mysql.connector.connect(host='localhost',user='root',password='system',db='nagu'):
    cursor=mydb.cursor(buffered=True)
    cursor.execute("create table if not exists registrations(username varchar(50) primary key,mobile varchar(20) unique,email varchar(50) unique,address varchar(50),password varchar(20))");
mycursor=mydb.cursor()
@app.route('/reg',methods=['GET','POST'])
def reg():
    if request.method=='POST':
        username=request.form.get('username')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        address=request.form.get('address')
        password=request.form.get('password')
        otp=genotp()
        sendmail(to=email,subject="thanks for registration",body=f'otp is :{otp}')
        return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)

    return render_template('reg.html') 
@app.route('/otp/<username>/<mobile>/<password>/<address>/<email>/<otp>',methods=['GET','POST'])
def otp(username,mobile,email,address,password,otp):
    if request.method=='POST':
        uotp=request.form['uotp']
        print(uotp)
        if otp==uotp:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into registrations values(%s,%s,%s,%s,%s)',[username,mobile,email,address,password])
            mydb.commit()
            cursor.close()
            return redirect(url_for('home1'))
        
    return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from registrations where username=%s && password=%s',[username,password])
        data=cursor.fetchone()[0]
        print(data)
        if data==1:
            session['username']=username
            if not session.get(session['username']):
                session[session['username']]={}
    
            return redirect(url_for('homepage'))
        else:
            return 'Invalid username and password'
    return render_template('login.html') 

@app.route('/logout') 
def logout():
    if session.get('username'):
        session.pop('username')
    return redirect(url_for('login'))

@app.route('/homepage')
def homepage():
    return  render_template('homepage.html')
@app.route('/home1')
def home1():
    return  render_template('home1.html')

@app.route('/addpost',methods=['GET','POST'])
def add_post():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into posts (title,content,slug) values (%s,%s,%s)',(title,content,slug))
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_posts'))
    return render_template('add_post.html')
#create admin page
@app.route('/admin')
def admin():
    return render_template('admin.html')
#view posts
@app.route('/view_posts')
def view_posts():
    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT * from posts")
    posts=cursor.fetchall()
    print(posts)
    cursor.close()
    return render_template('view_posts.html',posts=posts)
#delete a posts
@app.route('/delete_post/<int:id>',methods=['POST'])
def delete_post(id):
    cursor = mydb.cursor(buffered=True)
    cursor.execute('select * from posts where id=%s',(id,))
    post=cursor.fetchone()
    cursor.execute('DELETE FROM posts where id=%s',(id,))
    mydb.commit()
    cursor.close()
    return redirect(url_for('view_posts'))
@app.route('/update_post/<int:id>',methods=['GET','POST'])
def update_post(id):
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor = mydb.cursor(buffered=True)
        cursor.execute('UPDATE posts set title=%s,content=%s,slug=%s where id=%s',(title,content,slug,id))
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_posts'))
    else:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select * from posts where id=%s',(id,))
        post=cursor.fetchone()
        mydb.commit()
        cursor.close()
        return render_template('update.html',post=post)



app.run(debug=True,use_reloader=True)

