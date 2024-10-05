from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/parking-details')
def parking_details():
    return render_template('parking-details.html')

@app.route('/sign-in')
def sign_in():
    return render_template('sign-in.html')

if __name__ == '__main__':
    app.run(debug=True)