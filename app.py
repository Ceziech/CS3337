from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime, timedelta
import os
import re
import stripe

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'GIGASECRETKEY'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://zork:cnHjpkHPDWxrjRb9Vx1P@parking-db.c766iu0ku433.us-west-2.rds.amazonaws.com:5432/parking_db')
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

# Ticket model
class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    license_plate = db.Column(db.String(20), db.ForeignKey('vehicles.license_plate'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('tickets', lazy=True))
    vehicle = db.relationship('Vehicle', backref=db.backref('tickets', lazy=True))

    def __repr__(self):
        return f'<Ticket {self.id} - License Plate: {self.license_plate}, Amount: {self.amount}>'

# Endpoint to add a ticket
@app.route('/admin/add_ticket', methods=['POST'])
def add_ticket():
    if not session.get('is_admin'):  # Ensure only admins can add tickets
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.json
    license_plate = data.get('license_plate')
    amount = data.get('amount')
    comments = data.get('comments')

    vehicle = Vehicle.query.filter_by(license_plate=license_plate).first()
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    new_ticket = Ticket(
        license_plate=license_plate,
        user_id=vehicle.user_id,
        amount=amount,
        comments=comments
    )
    db.session.add(new_ticket)
    db.session.commit()
    
    return jsonify({'success': True, 'ticket_id': new_ticket.id})

    
class Permit(db.Model):
    __tablename__ = 'permits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique identifier for the permit
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Reference to the user
    permit_type = db.Column(db.String(50), nullable=False)  # Type of permit (e.g., event, athletic)
    start_date = db.Column(db.Date, nullable=False)  # Start date of the permit
    end_date = db.Column(db.Date, nullable=False)  # End date of the permit
    price = db.Column(db.Float, nullable=False)  # Price of the permit

    # Define the relationship with the User table
    user = db.relationship('User', backref=db.backref('permits', lazy=True))

    def __repr__(self):
        return f"<Permit {self.permit_type} for User {self.user_id}, valid from {self.start_date} to {self.end_date}>"


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



def calculate_permit_dates(permit_type):
    start_date = datetime.now().date()
    if permit_type == "event" or permit_type == "athletic":
        end_date = start_date  # Single-day permits
    elif permit_type == "2wheel":
        end_date = datetime(start_date.year, 12, 31).date()  # End of Fall semester
    elif permit_type == "highschool":
        end_date = datetime(start_date.year, 12, 31).date()  # End of Fall semester
    elif permit_type == "nonaffiliated":
        end_date = start_date + timedelta(days=30)  # 30-day permit
    else:
        raise ValueError("Unknown permit type")
    return start_date, end_date

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

@app.route('/appeals_ticket', methods=['GET', 'POST'])
def appeals_ticket():
    if 'user_id' not in session:
        flash("Please log in to appeal a ticket", "warning")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
       
        flash("Thank you for your appeal request. We will get to it soon.", "success")
       
        return render_template('appeals_ticket.html')
    
    return render_template('appeals_ticket.html')

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

stripe.api_key = "sk_test_51QSwV5RptQOte5PD2yrLVjo5qgTjJ3g0YdkKoMhKEj9Ey7SE8xINW8DkqpiVIXvv8v3tKibpr6LoTY3VUUHol8wt00Kwulp5Ae"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # Extract permit type from the POST request
        data = request.json
        permit_type = data.get('permit_type', '')

        # Define pricing based on permit type
        permit_prices = {
            'event': 'price_1QSwg6RptQOte5PDjaXCvtqF',  # Example Stripe price ID
            'athletic': 'price_1QSwhARptQOte5PD4fZ4SJAe',
            '2wheel': 'price_1QSwhvRptQOte5PDkTYfjrph',
            'highschool': 'price_1QSwiHRptQOte5PDMTFSDSIj',
            'nonaffiliated': 'price_1QSwifRptQOte5PDduZdgV6D',
            'ticket': 'price_1QT9H2RptQOte5PDU8HbvA6d '
        }

        # Get the price ID for the selected permit
        price_id = permit_prices.get(permit_type)
        if not price_id:
            return jsonify({'error': 'Invalid permit type selected'}), 400

        # Create the checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )

        return jsonify({'success': True, 'redirect_url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        # Get cart and email from the frontend
        data = request.json
        cart = data.get('cart', [])
        email = data.get('email')

        # if not cart or not email:
        #     return jsonify({"error": "Invalid request. Cart or email missing."}), 400

        # Calculate total amount in cents (including tax)
        total_amount = int(sum(float(item['price']) for item in cart) * 1.1 * 100)  # 10% tax

        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='usd',
            receipt_email=email,  # Send a receipt to the provided email
            automatic_payment_methods={"enabled": True},  # Enable automatic payment methods
        )

        return jsonify({'clientSecret': intent['client_secret']})  # Send client_secret to frontend
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/lookup_ticket', methods=['POST'])
def lookup_ticket():
    try:
        data = request.json
        ticket_number = data.get('ticketNumber')
        plate_or_vin = data.get('plateOrVin')

        if not ticket_number and not plate_or_vin:
            return jsonify({'error': 'Please provide either a ticket number or a plate/VIN.'}), 400

        # Query the ticket based on ticket number or license plate
        ticket = None
        if ticket_number:
            ticket = Ticket.query.filter_by(id=ticket_number).first()
        elif plate_or_vin:
            ticket = Ticket.query.filter_by(license_plate=plate_or_vin).first()

        if not ticket:
            return jsonify({'error': 'Ticket not found.'}), 404

        ticket_data = {
            'id': ticket.id,
            'license_plate': ticket.license_plate,
            'amount': float(ticket.amount),
            'comments': ticket.comments,
            'date': ticket.date.isoformat()
        }

        return jsonify({'ticket': ticket_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/payment-success', methods=['POST'])
def payment_success():
    try:
        data = request.json
        cart = data.get('cart', [])

        # Ensure user exists
        user = User.query.filter_by(id=session['user_id']).first()
        if not user:
            return jsonify({"error": "User not found"}), 400

        permits_created = []
        total_ticket_payment = 0  # To track ticket payments

        # Process each item in the cart
        for item in cart:
            app.logger.info(f"Processing item: {item}")
            if not isinstance(item, dict):
                app.logger.error(f"Invalid item in cart: {item}")
                raise ValueError("Invalid item in cart")

            item_name = item['name']
            price = item['price']

            if item_name.startswith("Ticket #"):  # Check if the item is a ticket
                total_ticket_payment += price  # Add ticket amount to the total
            else:
                # Handle permit logic (unchanged)
                permit_type = item_name
                start_date, end_date = calculate_permit_dates(permit_type)

                new_permit = Permit(
                    user_id=user.id,
                    permit_type=permit_type,
                    start_date=start_date,
                    end_date=end_date,
                    price=price
                )
                db.session.add(new_permit)
                permits_created.append({
                    "id": new_permit.id,
                    "user_id": new_permit.user_id,
                    "permit_type": new_permit.permit_type,
                    "start_date": new_permit.start_date.isoformat(),
                    "end_date": new_permit.end_date.isoformat(),
                    "price": new_permit.price
                })

        # Subtract ticket payments from user's currently_due
        if total_ticket_payment > 0:
            user.currently_due -= total_ticket_payment
            if user.currently_due < 0:
                user.currently_due = 0  # Prevent negative balances

        db.session.commit()

        app.logger.info(f"Permits created: {permits_created}")
        app.logger.info(f"Total ticket payment deducted: ${total_ticket_payment:.2f}")
        return jsonify({
            "success": True,
            "message": f"Payment processed successfully! Tickets: ${total_ticket_payment:.2f}, Permits created: {len(permits_created)}",
            "currently_due": user.currently_due,
            "permits": permits_created
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing payment success: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/cancel')
def cancel():
    return "Payment canceled. Please try again."

if __name__ == '__main__':
    app.run(debug=True)



# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
