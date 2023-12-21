from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route('/')
def default():
  return 'Login Page'

@app.route('/index')
def index():
  return redirect(url_for('default'))


@app.route('/home')
def home():
  return 'This is Home page'

@app.route('/management')
def management():
  return 'this is management page'

@app.errorhandler(404)
def not_found(error):
  return 'Page Not Found'


if __name__ == '__main__':
  app.run(debug = True)