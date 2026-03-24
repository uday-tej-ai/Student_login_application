import sqlite3

from flask import Flask, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "SAY_MY_NAME!"


def get_db_connection():
    # Added timeout to help prevent the "Locked" error
    conn = sqlite3.connect("database.db", timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def welcome():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template("welcome.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fix: Check the database for existing user, not the empty dictionary
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()  # Always close before returning
            return "User already exists! <a href='/register'>Try again</a>"

        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        conn.close()  # FIX: This releases the lock so Login can work

        return redirect(url_for('login'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fix: Check the Database, because student_d is always empty on restart
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()  # Close immediately after fetching

        if user:
            session['user'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials! Please try again.", "error")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", student=session['user'])
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)