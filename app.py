from flask import Flask,request, render_template, flash, redirect, url_for, session, logging 
from wtforms import Form,StringField,IntegerField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import sqlite3,os
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

app=Flask(__name__)

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower()



baj=sqlite3.connect('bajrang.db')
baj.execute('CREATE TABLE IF NOT EXISTS BAJRANG_DAL (USER TEXT NOT NULL, LOCATION TEXT NOT NULL, ACTIVITY TEXT NOT NULL) ;')
baj.close()

class BajrangForm(Form):
	location=StringField('Location: ', [validators.Length(min=2,max=100)])
	activity=StringField('Post Activity Details: ', [validators.Length(min=2,max=1000)])

app.config.update(
	DEBUG=True,
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'itcoupledal@gmail.com',
	MAIL_PASSWORD = 'coupledal'
	)
mail = Mail(app)

conn=sqlite3.connect('user_database.db')

conn.execute('CREATE TABLE IF NOT EXISTS COUPLES \
			(NAME1 	TEXT NOT NULL,\
			 SCREEN1  TEXT NOT NULL ,\
			 EMAIL1   TEXT NOT NULL ,\
			 AGE1 INT NOT NULL,\
			 INTEREST1 TEXT,\
			 NAME2 	TEXT NOT NULL,\
			 SCREEN2  TEXT NOT NULL,\
			 EMAIL2   TEXT NOT NULL,\
			 AGE2 INT NOT NULL,\
			 INTEREST2 TEXT,\
			 PASSWORD TEXT,\
			 VALIDATED1 INT,\
			 VALIDATED2 INT,\
			 LOG INT,\
			 IMAGE TEXT,\
			 PRIMARY KEY(EMAIL1,EMAIL2)\
			 );')

conn.execute('CREATE TABLE IF NOT EXISTS FRIENDS (FRIEND1 TEXT NOT NULL, FRIEND2 TEXT NOT NULL);')

conn.close()

conn=sqlite3.connect('reso_name.db')

conn.execute('CREATE TABLE IF NOT EXISTS reviews \
			(NAME 	TEXT NOT NULL,\
			 REVIEW  TEXT NOT NULL \
			 );')

conn.close()


class RegisterForm(Form):
	name1=StringField('Your Name: ', [validators.Length(min=2,max=100)])
	screen1=StringField('Your Screen Name: ', [validators.Length(min=2,max=100)])
	email1=StringField('Your email: ',[validators.Length(min=7,max=100)])
	age1=IntegerField('Your age(years): ',[validators.required()])
	interest1=TextAreaField('Your Interest: ',[validators.Length(min=1,max=1000)])
	name2=StringField('Bae\'s Name: ', [validators.Length(min=2,max=100)])
	screen2=StringField('Bae\'s Screen Name: ', [validators.Length(min=2,max=100)])
	email2=StringField('Bae\'s email:',[validators.Length(min=7,max=100)])
	age2=IntegerField('Bae\'s age(years): ',[validators.required()])
	interest2=TextAreaField('Bae\'s Interest: ',[validators.Length(min=1,max=1000)])
	password=PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm',message='Passwords do not match')
		])
	confirm=PasswordField('Confirm Password')

class LoginForm(Form):
	email=StringField('Email: ',[validators.Length(min=7,max=100)])
	password=PasswordField('Password', [
		validators.DataRequired()])

class AddRestro(Form):
	name=StringField('Name: ',[validators.Length(min=2,max=100)])
	details=TextAreaField('Details: ', [
		validators.DataRequired()])

class AddHotel(Form):
	name=StringField('Name: ',[validators.Length(min=2,max=100)])
	details=TextAreaField('Details: ', [
		validators.DataRequired()])

class ReviewsForm(Form):
	review=TextAreaField('Review: ', [
		validators.DataRequired()])

@app.route('/')
@app.route('/index')
def index():
	return render_template('home.html')

@app.route('/succesFullRegister')
def succesFullRegister():
	return render_template('EmailSend.html')

@app.route('/EmailConfirmed')
def EmailConfirmed():
	return render_template('EmailConfirmed.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/TandC')
def TandC():
	return render_template('TandC.html')	

@app.route('/confirmation1/<email> <int:w>')
def confirmation1(email,w):
	con=sqlite3.connect("user_database.db")
	conn=con.cursor()
	if w==1:
		a='UPDATE COUPLES SET VALIDATED1=1 WHERE EMAIL1="%s";' %email
		conn.execute(a)
		con.commit()
	else:
		a='UPDATE COUPLES SET VALIDATED2=1 WHERE EMAIL2="%s";' %email
		conn.execute(a)
		con.commit()
	return redirect(url_for('EmailConfirmed'))


@app.route('/login',methods=['GET','POST'])
def login():
	con=sqlite3.connect("user_database.db")
	conn=con.cursor()
	res=conn.execute('''SELECT * FROM COUPLES WHERE LOG=1 ''')
	k=res.fetchone()
	if k!=None:
		conn.execute('''UPDATE COUPLES SET LOG=0''')
		con.commit()
	form=LoginForm(request.form)
	if request.method=='POST' and form.validate():
		email=form.email.data
		password=form.password.data
		con=sqlite3.connect("user_database.db")
		conn=con.cursor()
		res=conn.execute('''SELECT PASSWORD FROM COUPLES WHERE (EMAIL1=? OR EMAIL2=?) AND VALIDATED1=1 AND VALIDATED1=1;''',(email,email))
		k=res.fetchone()
		if k== None:
			flash('Email(s) verification pending!!!')
		else:
			for row in k:
				c= row
			d=sha256_crypt.verify(password,c)	
			if d==False:
				flash('Wrong Email or Password!!!')
				return render_template('login.html',form=form)
			else:
				conn.execute('''UPDATE COUPLES SET LOG=1 WHERE EMAIL1=? OR EMAIL2=?;''',(email,email))
				con.commit()
				return redirect(url_for('logged',email=email))
	return render_template('login.html',form=form)


@app.route('/register',methods=['GET','POST'])
def register():
	con=sqlite3.connect("user_database.db")
	conn=con.cursor()
	res=conn.execute('''SELECT * FROM COUPLES WHERE LOG=1 ''')
	k=res.fetchone()
	if k!=None:
		conn.execute('''UPDATE COUPLES SET LOG=0''')
		con.commit()
	form=RegisterForm(request.form)
	if request.method=='POST' and form.validate():
		name1=form.name1.data
		screen1=form.screen1.data
		email1=form.email1.data
		age1=form.age1.data
		interest1=form.interest1.data
		name2=form.name2.data
		screen2=form.screen2.data
		email2=form.email2.data
		age2=form.age2.data
		interest2=form.interest2.data
		password=sha256_crypt.encrypt(str(form.password.data))
		validated1=0
		validated2=0
		image='images/default.jpeg'

		if email1==email2:
			flash('Emails Cannot Be Same')
			return render_template('register.html',form=form)

		con=sqlite3.connect("user_database.db")
		conn=con.cursor()
		res=conn.execute('''SELECT * FROM COUPLES WHERE EMAIL1=?;''',(email1,))
		k=res.fetchone()

		if k != None:
			flash('Email Already Exists')
			return render_template('register.html',form=form)

		res=conn.execute('''SELECT * FROM COUPLES WHERE EMAIL2=?;''',(email2,))
		k=res.fetchone()

		if k != None:
			flash('Email Already Exists')
			return render_template('register.html',form=form)

		res=conn.execute('''SELECT * FROM COUPLES WHERE EMAIL1=?;''',(email2,))
		k=res.fetchone()

		if k != None:
			flash('Email Already Exists')
			return render_template('register.html',form=form)

		res=conn.execute('''SELECT * FROM COUPLES WHERE EMAIL2=?;''',(email1,))
		k=res.fetchone()

		if k != None:
			flash('Email Already Exists')
			return render_template('register.html',form=form)
	

		conn.execute("INSERT INTO COUPLES (NAME1, SCREEN1, EMAIL1, AGE1, INTEREST1, NAME2, SCREEN2, EMAIL2, AGE2, INTEREST2, PASSWORD, VALIDATED1,VALIDATED2,LOG,IMAGE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
			(name1,screen1,email1,age1,interest1,name2,screen2,email2,age2,interest2,password,validated1,validated2,validated2,image))
		
		con.commit()

		msg = Message("Couple Dal confirmation mail",
		sender="itcoupledal@gmail.com",
		recipients=[email1])
		link=url_for('confirmation1',email=email1,w=1,_external=True)
		msg.body="Click on the given link to confirm your account {}".format(link)
		mail.send(msg)

		msg = Message("Couple Dal confirmation mail",
		sender="itcoupledal@gmail.com",
		recipients=[email2])
		link=url_for('confirmation1',email=email2,w=2,_external=True)
		msg.body="Click on the given link to confirm your account {}".format(link)
		mail.send(msg)
		return redirect(url_for('succesFullRegister'))

	return render_template('register.html',form=form)	

@app.route('/logged/<email>/Bajrang',methods=['GET','POST'])
def bajrang(email):
	bajr=sqlite3.connect("bajrang.db")
	bajj=bajr.cursor()
	form=BajrangForm(request.form)
	if request.method=='POST' and form.validate():
		activity=form.activity.data
		location=form.location.data
		userdb=sqlite3.connect("user_database.db")
		userdata=userdb.cursor()
		use= userdata.execute('SELECT SCREEN1 FROM COUPLES WHERE EMAIL1==?',(email,))
		user=use.fetchone()
		if user==None:
			use= userdata.execute('SELECT SCREEN2 FROM COUPLES WHERE EMAIL2==?',(email,))
			user=use.fetchone()
		userdata.close()
		user=str(user)
		bajj.execute("INSERT INTO BAJRANG_DAL (USER,LOCATION,ACTIVITY) VALUES (?,?,?)",
			(user,location,activity))
		bajr.commit()
	bajr.close()
	bajr=sqlite3.connect("bajrang.db")
	bajj=bajr.cursor()
	bajj.execute("SELECT * FROM BAJRANG_DAL")
	r=bajj.fetchall()
	bajr.close()
	r.reverse()
	l=[]
	for row in r:
		li=list(row)
		li[0]=str(li[0])
		li[0]=li[0][3:-3]
		l.append(li)
	return render_template('bajrang.html',form=form,r=l,email=email)

@app.route('/logged/<email>/Hickey')
def hickey(email):
	bajr=sqlite3.connect("reso_name.db")
	bajj=bajr.cursor()
	bajj.execute("SELECT * FROM reso")
	r=bajj.fetchall()
	bajr.close()
	bajr=sqlite3.connect("reso_name.db")
	bajj=bajr.cursor()
	bajj.execute("SELECT * FROM hotel")
	h=bajj.fetchall()
	bajr.close()
	return render_template('hickey.html',r=r,h=h,email=email)

@app.route('/logged/<email>/<name>',methods=['GET','POST'])
def reviews(email,name):
	bajr=sqlite3.connect("reso_name.db")
	bajj=bajr.cursor()
	statement='SELECT review FROM reviews where name="'+name+'";'
	bajj.execute(statement)
	r=bajj.fetchall()
	l=[]
	for row in r:
		row=str(row)
		row=row[3:-3]
		l.append(row)
	bajr.close()
	bajr=sqlite3.connect("reso_name.db")
	bajj=bajr.cursor()
	statement='SELECT * FROM reso where name="'+name+'";'
	bajj.execute(statement)
	row=bajj.fetchone()
	if row==None:
		statement='SELECT * FROM hotel where name="'+name+'";'
		bajj.execute(statement)
		row=bajj.fetchone()
	if row==None:
		statement='SELECT * FROM sex where name="'+name+'";'
		bajj.execute(statement)
		row=bajj.fetchone()
	bajr.close()
	bajr=sqlite3.connect("reso_name.db")
	bajj=bajr.cursor()
	form=ReviewsForm(request.form)
	if request.method=='POST' and form.validate():
		review=form.review.data
		bajj.execute("INSERT INTO reviews (name,review) VALUES (?,?)",(name,review))
		bajr.commit()
		return redirect(url_for('reviews',email=email,name=name))
	return render_template('reviews.html',email=email,name=name,row=row,r=l,form=form)

@app.route('/logged/<email>/addRestro',methods=['GET','POST'])
def addRestro(email):
	form=AddRestro(request.form)
	con=sqlite3.connect('reso_name.db')
	conn=con.cursor()
	if request.method=='POST':
		if form.validate():
			name=form.name.data
			details=form.details.data
			if 'file' not in request.files:
				conn.execute('insert into reso (name,image,details) values (?,"default.jpeg",?)',(name,details))
				con.commit()
				return redirect(url_for('hickey',email=email))
			file = request.files['file']
			if file.filename == '':
				return redirect(url_for('hickey',email=email))
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				conn.execute('insert into reso (name,image,details) values (?,?,?)',(name,filename,details))
				con.commit()
				return redirect(url_for('hickey',email=email))

	return render_template('addRestro.html',form=form,email=email)

@app.route('/logged/<email>/addHotel',methods=['GET','POST'])
def addHotel(email):
	form=AddHotel(request.form)
	con=sqlite3.connect('reso_name.db')
	conn=con.cursor()
	if request.method=='POST':
		if form.validate():
			name=form.name.data
			details=form.details.data
			if 'file' not in request.files:
				conn.execute('insert into hotel (name,image,details) values (?,"defhot.jpg",?)',(name,details))
				con.commit()
				return redirect(url_for('hickey',email=email))
			file = request.files['file']
			if file.filename == '':
				return redirect(url_for('hickey',email=email))
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				conn.execute('insert into hotel (name,image,details) values (?,?,?)',(name,filename,details))
				con.commit()
				return redirect(url_for('hickey',email=email))

	return render_template('addHotel.html',form=form,email=email)

@app.route('/addFriend/<addToHim> <addHim>')
def addFriend(addToHim,addHim):
	con=sqlite3.connect("user_database.db")
	conn=con.cursor()
	q='select email1 from couples where email1="'+addToHim+'" or email2="'+addToHim+'"'+';'
	res=conn.execute(q)
	a=res.fetchone()
	first=a[0]
	q='select email1 from couples where email1="'+addHim+'" or email2="'+addHim+'"'+';'
	res=conn.execute(q)
	a=res.fetchone()
	second=a[0]
	conn.execute("INSERT INTO FRIENDS (FRIEND1,FRIEND2) VALUES (?,?)",
			(first,second))
	con.commit()
	return redirect(url_for('logged',email=addToHim))

@app.route('/Logout/<email>')
def logout(email):
	con=sqlite3.connect("user_database.db")
	conn=con.cursor()
	conn.execute("UPDATE COUPLES SET LOG=0 WHERE EMAIL1=? OR EMAIL2=?",(email,email))
	con.commit()
	return redirect(url_for('index'))

@app.route('/logged/<email>',methods=['GET','POST'])
def logged(email):
	con=sqlite3.connect("user_database.db")
	conn=con.cursor()
	conn.execute("SELECT * FROM COUPLES WHERE email1=? OR EMAIL2=?",(email,email))
	k=conn.fetchall()
	for row in k:
		c=row
	if c[13]==0:
		return 'Already Signed In'
	conn.execute("SELECT * FROM COUPLES WHERE email1!=? AND EMAIL2!=?",(email,email))	
	r=conn.fetchall()
	conn.execute("SELECT FRIEND2 FROM FRIENDS WHERE FRIEND1=?",(c[2],))
	dd=conn.fetchall()
	d=[]
	for entry in dd:
		entry=str(entry)
		entry=entry[3:len(entry)-3]
		d.append(entry)

	conn.execute("SELECT FRIEND1 FROM FRIENDS WHERE FRIEND2=?",(c[2],))
	dd=conn.fetchall()
	e=[]
	for entry in dd:
		entry=str(entry)
		entry=entry[3:len(entry)-3]
		e.append(entry)
	
	if request.method=='POST':
		if 'file' not in request.files:
			return redirect(url_for('logged',email=email))
		file = request.files['file']
		if file.filename == '':
			return redirect(url_for('logged',email=email))
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			con=sqlite3.connect("user_database.db")
			conn=con.cursor()
			statement="UPDATE COUPLES SET IMAGE='"+str(filename)+"' where email1='"+email+"' or email2='"+email+"'"
			conn.execute(statement)
			con.commit()
			return redirect(url_for('logged',email=email))

	return render_template("homeLog.html",c=c,r=r,email=email,d=d,e=e)

if __name__ == '__main__':
	app.secret_key='RadheRadhe'
	app.run(debug=True)