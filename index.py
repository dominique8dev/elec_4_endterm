from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'  # Change it based on your MySQL host
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'elec_4'
mysql = MySQL(app)

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    if not session.get("username"):
        return redirect(url_for("login"))
    return redirect(url_for("home"))

@app.route('/login')
def login():
    # redirect if authenticated
    if session.get('username'):
        return redirect(url_for('home'))
    return render_template('login.html', title="Login")

@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check for empty fields
    if not username:
        return render_template('login.html', error='Username is required.', title="Login")
    elif not password:
        return render_template('login.html', error='Password is required.', title="Login")

    # Connect to MySQL and check username and password
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s and password=%s", (username, password))
    result = cursor.fetchone()

    if result:
        # Save Session
        session['username'] = request.form.get('username')
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error='Incorrect username or password.', title="Login")


@app.route('/home')
def home():
    # Redirect if not authenticated
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('home.html', title="Home")

@app.route('/management')
def management():
    # Redirect if not authenticated
    if not session.get('username'):
        return redirect(url_for('login'))

    # Retrieve all Quotes
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT quotes.*, categories.id, categories.name FROM quotes INNER JOIN categories on quotes.category_id = categories.id ORDER BY updated_at desc")
    result = cursor.fetchall()

    return render_template('management.html', quotes = result, title="Management")

@app.route('/add_quote')
def add_quote():
    # Redirect if not authenticated
    if not session.get('username'):
        return redirect(url_for('login'))

    # Retrieve all categories
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    # Convert the tuple to a list
    categories_list = list(categories)

    return render_template('add_quote.html', categories=categories_list, title="Add Quote")



@app.route('/insert_quote', methods=['POST'])
def insert_quote():
    # Redirect if not authenticated
    if not session.get('username'):
        return redirect(url_for('login'))

    # Retrieve quote data from the form
    category_id = request.form.get('category')
    content = request.form.get('content')
    author = request.form.get('author')

    # print("Received:", category_id, content, author)

    # Insert the new quote into the database
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO quotes (category_id, content, author) VALUES (%s, %s, %s)", (category_id, content, author))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('management'))



@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM quotes WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect('/management')

@app.route('/edit_quote/<int:id>')
def edit_quote(id):
    # Redirect if not authenticated
    if not session.get('username'):
        return redirect(url_for('login'))

    # Retrieve the quote for editing
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM quotes WHERE id=%s", (id,))
    quote = cursor.fetchone()

    # Retrieve all categories
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    cursor.close()

    if quote:
        return render_template('edit_quote.html', quote=quote, categories=categories, title="Edit Quote")
    else:
        return "Quote not found"


@app.route('/update_quote/<int:id>', methods=['POST'])
def update_quote(id):
    # Redirect if not authenticated
    if not session.get('username'):
        return redirect(url_for('login'))

    # Retrieve updated quote data from the form
    category_id = request.form.get('category') 
    content = request.form.get('content')
    author = request.form.get('author')

    # Update the quote in the database
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE quotes SET category_id=%s, content=%s, author=%s WHERE id=%s", (category_id, content, author, id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('management'))

@app.route('/view_quote/<int:id>')
def view_quote(id):
    # Redirect if not authenticated
    if not session.get('username'):
        return redirect(url_for('login'))

    # Retrieve the specific quote for viewing
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM quotes WHERE id=%s", (id,))
    quote = cursor.fetchone()
    cursor.close()

    if quote:
        return render_template('view_quote.html', quote=quote, title="View Quote")
    else:
        return "Quote not found"

@app.route('/logout', methods=['POST'])
def logout():
    session['username'] = None
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

# Run App
if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)