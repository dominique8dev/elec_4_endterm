from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'  # Change it based on your MySQL host
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'elec_4'

mysql = MySQL(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return redirect(url_for('login'))


@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check for empty fields
    if not username:
        return render_template('login.html', error='Username is required.')
    elif not password:
        return render_template('login.html', error='Password is required.')

    # Connect to MySQL and check username and password
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result and password == result[0]:
        return redirect(url_for('home'))
    elif result is None:
        return render_template('login.html', error='Incorrect Username.')
    elif password != result[0]:
        return render_template('login.html', error='Incorrect Password.')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/management')
def management():
    return render_template('management.html')

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found"

if __name__ == '__main__':
    app.run(debug=True)