from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)

app.secret_key = "SAY_MY_NAME!"

student_d = {}


@app.route('/welcome')
def welcome():
    # If the user is already logged in, send them straight to the dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template("welcome.html")
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in student_d:
            return "User already exists! <a href='/register'>Try again</a>"

        student_d[username] = password
        print(f"User Registered: {username}")

        # After registering, go to the Login page
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in student_d and student_d[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials! <a href='/login'>Try again</a>"

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        current_student = session['user']
        return render_template("dashboard.html", student=current_student)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)