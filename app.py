from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import re

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
@app.route('/')
@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template('home.html')

@app.route('/parking')
def parking():
    return render_template('parking.html')

@app.route('/parking-details')
def parking_details():
    return render_template('parking-details.html')

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if len(name) < 2 or len(name) > 50 or not re.match("^[A-Za-z0-9]+$", name):
            return "Invalid Name. Please ensure the name is between 1-50 characters.", 400

        email_regex = r="^[^\s@]+@[^\s@]+\.[^\s@]+$";
        if not re.match(email_regex, email):
            return "Invalid email. Please enter a valid email.", 400

        if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[!@#$%^&*]", password):
            return "Invalid password. Must contain at least 8 characters, 1 special character and 1 number.", 400

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        session['username'] = new_user.name
        return redirect(url_for('home'))
    return render_template('sign-in.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.name
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)