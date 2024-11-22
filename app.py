from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from twilio.rest import Client
import os
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'GIGASECRETKEY'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'database link')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    currently_due = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'<User {self.name}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    trans_id = db.Column(db.Integer, primary_key=True)  # Primary Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign Key
    amount = db.Column(db.Integer, nullable=False)  # Transaction amount
    date = db.Column(db.Date, default=db.func.current_date())  # Use DATE datatype
    # description = db.Column(db.String(255), nullable=True)  # Optional description

    # Define the relationship
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.trans_id}, Amount: {self.amount}>'

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    link = db.Column(db.String(255), nullable=False)  # Link to the event details page
    posted_on = db.Column(db.DateTime, default=db.func.now())  # When the event was created

    def __repr__(self):
        return f'<Event {self.title}>'

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    license_plate = db.Column(db.String(20), primary_key=True)  # Primary Key
    vehicle_type = db.Column(db.String(50), nullable=False)    # Vehicle type (e.g., car, truck)
    make = db.Column(db.String(50), nullable=False)            # Manufacturer
    model = db.Column(db.String(50), nullable=False)           # Model of the vehicle
    year = db.Column(db.Integer, nullable=False)               # Year of manufacturing
    color = db.Column(db.String(20), nullable=False)           # Color of the vehicle
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign Key to users table

    # Relationship to the User table
    user = db.relationship('User', backref=db.backref('vehicles', lazy=True))

    def __repr__(self):
        return f'<Vehicle {self.license_plate} - {self.make} {self.model}>'




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
            session['is_admin'] = user.is_admin  # Store admin status in session
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

    if data_type == 'personal_info':
        return jsonify({
            'data': {
                'name': user.name,
                'email': user.email,
                'phone': 'N/A',  # Replace with actual phone field if it exists
                'address': 'N/A'  # Replace with actual address field if it exists
            }
        })
    elif data_type == 'past_due':
        return jsonify({'data': user.currently_due})  # Mock data
    elif data_type == 'current_due':
        return jsonify({'data': user.currently_due})  # Mock data
    elif data_type == 'transaction_history':
        # Fetch transactions for the user
        transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
        transactions_data = [
            {
                'id': transaction.trans_id,
                'amount': transaction.amount,
                'date': transaction.date.isoformat()  # Convert to string format
            }
            for transaction in transactions
        ]
        return jsonify({'data': transactions_data})
    else:
        return jsonify({'error': 'Invalid data type requested'}), 400


class Appeal(db.Model):
    __tablename__ = 'appeals'
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='Pending') 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Appeal {self.ticket_number} - {self.status}>'

# class Vehicle(db.Model):
#     __tablename__ = 'vehicles'
#     license_plate = db.Column(db.String(20), primary_key=True)
#     vehicle_type = db.Column(db.String(50), nullable=False)
#     make = db.Column(db.String(50), nullable=False)
#     model = db.Column(db.String(50), nullable=False)
#     year = db.Column(db.Integer, nullable=False)
#     color = db.Column(db.String(20), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

@app.route('/manage_vehicle', methods=['GET', 'POST'])
def manage_vehicle():
    if 'user_id' not in session:
        flash("Please log in to manage your vehicles.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        license_plate = request.form['license_plate']
        vehicle_type = request.form['vehicle_type']
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        color = request.form['color']
        user_id = session['user_id']

        existing_vehicle = Vehicle.query.get(license_plate)
        if existing_vehicle:
            flash("Vehicle already exists with this license plate.", "danger")
        else:
            new_vehicle = Vehicle(
                license_plate=license_plate,
                vehicle_type=vehicle_type,
                make=make,
                model=model,
                year=year,
                color=color,
                user_id=user_id
            )
            db.session.add(new_vehicle)
            db.session.commit()
            flash("Vehicle added successfully.", "success")
        return redirect(url_for('manage_vehicle'))

    vehicles = Vehicle.query.filter_by(user_id=session['user_id']).all()
    return render_template('manage-vehicle.html', vehicles=vehicles)

@app.route('/delete_vehicle/<license_plate>', methods=['POST'])
def delete_vehicle(license_plate):
    if 'user_id' not in session:
        flash("Please log in to manage your vehicles.", "warning")
        return redirect(url_for('login'))

    vehicle = Vehicle.query.get(license_plate)
    if vehicle and vehicle.user_id == session['user_id']:
        db.session.delete(vehicle)
        db.session.commit()
        flash("Vehicle deleted successfully.", "success")
    else:
        flash("Unauthorized access or vehicle not found.", "danger")
    return redirect(url_for('manage_vehicle'))

@app.route('/fetch_vehicle', methods=['POST'])
def fetch_vehicle():
    license_plate = request.json.get('license_plate')
    vehicle = Vehicle.query.get(license_plate)
    if vehicle:
        vehicle_data = {
            'vehicle_type': vehicle.vehicle_type,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'color': vehicle.color
        }
        return jsonify(vehicle_data), 200
    return jsonify({'error': 'Vehicle not found'}), 404

@app.route('/appeal_ticket', methods=['GET', 'POST'])
def appeal_ticket():
    if 'user_id' not in session:
        flash("Please log in to appeal a ticket", "warning")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
       
        flash("Thank you for your appeal request. We will get to it soon.", "success")
       
        return render_template('appeal_ticket.html')
    
    return render_template('appeal_ticket.html')

def send_sms(to_number, message_body):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    
    ####### Send SMS
    message = client.messages.create(
        body=message_body,
        from_=os.getenv('TWILIO_PHONE_NUMBER'),
        to=to_number
    )
    return message.sid

@app.route('/purchase_ticket', methods=['POST'])
def purchase_ticket():
    if 'user_id' not in session:
        flash("Please log in to purchase a ticket", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)

    ###### Verify that the user has a valid phone number before continuing
    phone_number = '+12138224478'  ######## Replace with actual phone retrieval from user data table(Inprogress Hardcoded for now)

    if phone_number:
        ######## Send SMS confirmation
        message_body = "Your Parking purchase has been confirmed. Thank you for your purchase!"######Will add different option onto the message in later iteration
        try:
            send_sms(phone_number, message_body)
            flash("Ticket purchase confirmed. SMS confirmation sent.", "success")
        except Exception as e:
            flash(f"Failed to send SMS: {str(e)}", "danger")
    else:
        flash("No valid phone number provided for SMS confirmation.", "danger")

    return redirect(url_for('home'))
@app.route('/view_appeals')
def view_appeals():
    if 'user_id' not in session:
        flash("Please log in to view your appeals", "warning")
        return redirect(url_for('login'))
    
    appeals = Appeal.query.filter_by(user_id=session['user_id']).all()
    return render_template('view_appeals.html', appeals=appeals)

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

@app.route('/event-parking')
def event_parking():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('event-parking.html', events=events)


@app.route('/shop_cart_page')
def shop_cart_page():
    return render_template('shop_cart_page.html')

@app.route('/SampleEvent')
def SampleEvent():
    return render_template('SampleEvent.html')

@app.route('/view_transactions')
def view_transactions():
    if 'user_id' not in session:
        flash("Please log in to view transactions.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    return render_template('view_transactions.html', transactions=transactions)

@app.route('/admin/events', methods=['GET', 'POST'])
def manage_events():
    if 'admin_id' not in session:  # Check if the user is logged in as admin
        # flash("You must be logged in as an admin to access this page.", "danger")
        # return redirect(url_for('login'))
        pass
    
    if request.method == 'POST':
        # Handle event creation
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        link = request.form['link']

        new_event = Event(title=title, description=description, date=date, link=link)
        db.session.add(new_event)
        db.session.commit()
        flash("Event added successfully.", "success")
        return redirect(url_for('manage_events'))

    # Fetch all events to display
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('admin_events.html', events=events)

@app.route('/admin/get_user', methods=['POST'])
def get_user():
    if not session.get('is_admin'):  # Ensure only admins can access this
        return jsonify({'error': 'Unauthorized access'}), 403

    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'currently_due': user.currently_due
    })

@app.route('/admin/edit_user', methods=['POST'])
def edit_user():
    if not session.get('is_admin'):  # Ensure only admins can access this
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.json
    user = User.query.get(data.get('id'))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update user information
    user.name = data.get('name')
    user.email = data.get('email')
    user.currently_due = data.get('currently_due')

    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/get_vehicle', methods=['POST'])
def get_vehicle():
    license_plate = request.json.get('license_plate')
    vehicle = Vehicle.query.filter_by(license_plate=license_plate).first()

    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    # Fetch the associated user's email
    user = User.query.get(vehicle.user_id)

    return jsonify({
        'license_plate': vehicle.license_plate,
        'vehicle_type': vehicle.vehicle_type,
        'make': vehicle.make,
        'model': vehicle.model,
        'year': vehicle.year,
        'color': vehicle.color,
        'user_email': user.email if user else 'Unknown'  # Include the user email
    })


@app.route('/admin/edit_vehicle', methods=['POST'])
def edit_vehicle():
    # if not session.get('is_admin'):  # Ensure only admins can access this
    #     return jsonify({'error': 'Unauthorized access'}), 403

    data = request.json
    vehicle = Vehicle.query.get(data.get('license_plate'))

    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    # Update vehicle information
    vehicle.vehicle_type = data.get('vehicle_type')
    vehicle.make = data.get('make')
    vehicle.model = data.get('model')
    vehicle.year = data.get('year')
    vehicle.color = data.get('color')

    db.session.commit()
    return jsonify({'success': True})



# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
