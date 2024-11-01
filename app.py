from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:342562@localhost:5432/users')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))  # Optional field for personal info
    address = db.Column(db.String(120))  # Optional field for personal info

    def __repr__(self):
        return f'<User {self.name}>'

# Home route
@app.route('/')
@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html', username=session['username'])
    return render_template('home.html')

# Sign-in route
@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if len(name) < 2 or len(name) > 50 or not re.match("^[A-Za-z0-9]+$", name):
            return "Invalid Name. Please ensure the name is between 1-50 characters.", 400

        email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
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

# Login route
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

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

# Route to get user data for the account information modal
@app.route('/get_user_data', methods=['POST'])
def get_user_data():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 403

    data_type = request.json.get('dataType')
    user_id = session['user_id']
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Example response data based on data type
    if data_type == 'personal_info':
        return jsonify({
            'data': {
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'address': user.address
            }
        })
    elif data_type == 'past_due':
        return jsonify({
            'data': '150.00'  # Mock amount due
        })
    elif data_type == 'current_due':
        return jsonify({
            'data': '75.00'  # Mock current due amount
        })
    elif data_type == 'transaction_history':
        return jsonify({
            'data': [
                'Payment of $50 on 2024-01-15',
                'Payment of $100 on 2024-02-20',
                'Payment of $75 on 2024-03-10'
            ]  # Mock transaction history
        })
    else:
        return jsonify({'error': 'Invalid data type requested'}), 400

# Other routes for additional pages
@app.route('/parking')
def parking():
    return render_template('parking.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/parking-details')
def parking_details():
    return render_template('parking-details.html')

@app.route('/tickets')
def tickets():
    return render_template('tickets.html')

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
