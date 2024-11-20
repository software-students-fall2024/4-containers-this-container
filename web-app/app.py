import secrets

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 

client = MongoClient("mongodb://mongodb:27017/")
db = client.user_database
users_collection = db.users
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({"_id": user_id})
    if user_data:
        return User(user_id=user_data["_id"], username=user_data["username"])
    return None

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('register'))

        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')

        users_collection.insert_one({"username": username, "password": hashed_password})

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = users_collection.find_one({"username": username})
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_id=str(user_data['_id']), username=user_data['username'])
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('home'))
        
        flash('Invalid username or password.')
    
    return render_template('login.html')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/')
def ini():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
