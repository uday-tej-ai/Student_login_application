import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "SAY_MY_NAME!"

# --- 1. SETUP FOLDERS ---
UPLOAD_FOLDER = 'static/profile_pics'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# --- 2. DATABASE LOGIC ---
def get_db_connection():
    conn = sqlite3.connect("database.db", timeout=20)
    conn.row_factory = sqlite3.Row
    # This creates the table WITH the profile_pic column automatically if it's missing
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        username
                        TEXT
                        NOT
                        NULL,
                        email
                        TEXT
                        NOT
                        NULL,
                        password
                        TEXT
                        NOT
                        NULL,
                        profile_pic
                        TEXT
                        DEFAULT
                        'default.png'
                    )''')
    return conn


# --- 3. ROUTES ---

@app.route('/')
def welcome():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template("welcome.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    #hgdhd
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return "User already exists! <a href='/register'>Try again</a>"

        # Explicitly adding 'default.png' for new users
        cursor.execute("INSERT INTO users (username, email, password, profile_pic) VALUES (?, ?, ?, ?)",
                       (username, email, password, 'default.png'))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "error")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        username = session['user']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profile_pic FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        conn.close()

        # Use the filename from DB or the default
        pic = user_row['profile_pic'] if user_row and user_row['profile_pic'] else 'default.png'
        return render_template("dashboard.html", student=username, profile_pic=pic)

    return redirect(url_for('login'))


@app.route('/edit_profile')
def edit_profile():
    if 'user' in session:
        return render_template("edit_profile.html", student=session['user'])
    return redirect(url_for('login'))


@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'user' in session:
        file = request.files.get('profile_image')
        if file and file.filename != '':
            username = session['user']
            filename = f"{username}_avatar.png"

            # Save the file
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            # Update Database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (filename, username))
            conn.commit()
            conn.close()

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# --- 4. START SERVER ---
if __name__ == '__main__':
    app.run(debug=True)