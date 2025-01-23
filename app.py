from flask import Flask, render_template, redirect, url_for, request, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize both databases
def init_databases():
    # Users database
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

    # Donations database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT NOT NULL,
                quantity TEXT NOT NULL,
                location TEXT NOT NULL
            )
        ''')
        conn.commit()

# Default route - Redirect to login if not logged in
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('index'))

# Homepage
@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate user
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            with sqlite3.connect('users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'error')
    return render_template('signup.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Donate route
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        food_name = request.form['food_name']
        quantity = request.form['quantity']
        location = request.form['location']
        # Save to database
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO donations (food_name, quantity, location) VALUES (?, ?, ?)',
                           (food_name, quantity, location))
            conn.commit()
        return render_template('donate.html', message="Donation added successfully!")
    return render_template('donate.html')

# Claim route
@app.route('/claim', methods=['GET', 'POST'])
def claim():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            donation_id = request.form.get('donation_id')
            # Delete the claimed food from the database
            cursor.execute('DELETE FROM donations WHERE id = ?', (donation_id,))
            conn.commit()
            message = "Food claimed successfully!"
        else:
            message = None
        # Fetch all available donations
        cursor.execute('SELECT * FROM donations')
        donations = cursor.fetchall()
    return render_template('claim.html', donations=donations, message=message)

if __name__ == '__main__':
    init_databases()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
