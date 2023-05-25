from flask import Flask,request,session, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,logout_user,login_manager,LoginManager,login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from flask_mail  import*
#import json

app = Flask("__name__")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/dbhos'
app.config['SQLALCHEMY_MODUFICATIONS'] = True
db = SQLAlchemy(app)

local_server = True
app.secret_key = 'altaf khan'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

#with open('config.json','r') as c:
 #   params = json.load(c)["params"]

app.config['MAIL_SERVER'] = 'smtp_gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'zahanaktar322@gmail.com'
app.config['MAIL_PASSWORD'] = 'lamfbnewbjueowsv'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(250))

class Patients(db.Model):
    pid = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    slot = db.Column(db.String(50))
    disease = db.Column(db.String(50))
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    dept = db.Column(db.String(50))
    phone = db.Column(db.String(50))

class Doctor(db.Model):
    dpid = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(50))
    dname = db.Column(db.String(50))
    dept = db.Column(db.String(50))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            msg = "Email Already exists"
            return render_template("signup.html", msg=msg)
        epassword = generate_password_hash(password)
        new_user = User(username=username,email=email,password=epassword)
        db.session.add(new_user)
        db.session.commit()
        msg = "Register Successfull"
        return render_template("login.html", msg=msg)
    return render_template("signup.html")

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            return redirect( url_for('home'))
        else:
            msg = "Email and password encorrect "
            return render_template("login.html",msg=msg)
    return render_template("login.html")

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect( url_for('login'))

@login_required
@app.route('/patient', methods=['GET','POST'])
def patient():
    doct = Doctor.query.all()
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        gender = request.form.get("gender")
        slot = request.form.get("slot")
        disease = request.form.get("disease")
        time = request.form.get("time")
        date = request.form.get("date")
        dept = request.form.get("dept")
        phone = request.form.get("phone")

        query = Patients(email=email,name=name,gender=gender,slot=slot,disease=disease,time=time,date=date,dept=dept,phone=phone)
        db.session.add(query)
        db.session.commit()
       # mail.send_message('HOSPITAL MANAGEMENT SYSTEM', sender='zahanaktar322@gmail.com', recipients=[email],
        #body="Your booking is confirm thank choosing Us ")
        msg = "Booking Cofirmed"

        return render_template("booking.html", msg=msg)
    return render_template('patient.html', doct=doct)

@login_required
@app.route("/booking")
def booking():
    em = current_user.email
    user = Patients.query.filter_by(email=em)
     #user = db.engine.echo(f"SELECT * FROM 'Patients' WHERE email='{em}")
    return render_template("booking.html",user=user)

@login_required
@app.route("/edit/<int:pid>", methods=['GET','POST'])
def edit(pid):
    pati = Patients.query.get_or_404(pid)
    if request.method == 'POST':
        pati.email = request.form.get("email")
        pati.name = request.form.get("name")
        pati.gender = request.form.get("gender")
        pati.slot = request.form.get("slot")
        pati.disease = request.form.get("disease")
        pati.time = request.form.get("time")
        pati.date = request.form.get("date")
        pati.dept = request.form.get("dept")
        pati.phone = request.form.get("phone")
        db.session.commit()
        
        msg = "Updated Data Successfully !"
        return render_template("booking.html", msg=msg)
    return render_template("edit.html", pati=pati)

@login_required
@app.route("/delete/<int:pid>", methods=['GET','POST'])
def delete(pid):
    pati = Patients.query.get_or_404(pid)
    db.session.delete(pati)
    db.session.commit()
    msg = "Data Deleted Successfull"
    return render_template("booking.html", msg=msg)

@app.route("/doctor", methods=['GET','POST'])
def doctor():
    if request.method == 'POST':
        email = request.form.get("email")
        dname = request.form.get("dname")
        dept = request.form.get("dept")

        dtr = Doctor(email=email,dname=dname,dept=dept)
        db.session.add(dtr)
        db.session.commit()
        msg = "Data Inserted Successfully "
        return render_template("doctor.html",msg=msg)
    return render_template("doctor.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)