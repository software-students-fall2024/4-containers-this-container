import secrets

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import ast

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 

client = MongoClient("mongodb://mongodb:27017/")
db = client.genre_detector
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
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_id=user_data["_id"], username=user_data["username"])
    return None

@app.route('/home')
@login_required
def home():
    cur_user = current_user.username
    cur_user_collection = db[cur_user]
    genre = getStats(cur_user_collection)
    recommendations = getRecommendations(genre)
    return render_template('home.html', genre = genre, recommendations = recommendations)

def getStats(cur_user_collection):
    pipeline = [
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}}
    ]
    genre_counts = list(cur_user_collection.aggregate(pipeline))

    total_songs = sum(item["count"] for item in genre_counts)

    result = [
        {
            "Name": item["_id"],
            "Amount": item["count"],
            "Percentage": f"{(item['count'] / total_songs) * 100:.2f}%"
        }
        for item in genre_counts
    ]

    return result

def getRecommendations(genre):
    sorted_genres = sorted(genre, key=lambda x: x["Amount"], reverse=True)
    
    if(len(sorted_genres) == 0):
        return []
    
    top_genre = sorted_genres[0] 
    second_genre = sorted_genres[1] if len(sorted_genres) > 1 else 0
    
    total_amount = top_genre["Amount"] + second_genre["Amount"]
    top_genre_count = round(5 * (top_genre["Amount"] / total_amount))
    second_genre_count = 5 - top_genre_count
    
    recommend_collection = db["recommendations"]
    
    top_genre_songs = list(
        recommend_collection.aggregate([
            {"$match": {"genre": top_genre["Name"]}},
            {"$sample": {"size": top_genre_count}}
        ])
    )
    second_genre_songs = list(
        recommend_collection.aggregate([
            {"$match": {"genre": second_genre["Name"]}},
            {"$sample": {"size": second_genre_count}}
        ])
    )

    combined_songs = top_genre_songs + second_genre_songs

    result = [
        {"Title": song["title"], "Artist": song["artist"], "Genre": song["genre"]}
        for song in combined_songs
    ]

    return result
    


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

        db.create_collection(username)
        
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

def addRecommendations():
    recommend_collection = db.recommendations
    
    with open("songs.txt", "r") as f:
        file_content = f.read()
    
    songs_dict = ast.literal_eval(file_content)
    songs = songs_dict if isinstance(songs_dict, list) else []


    if recommend_collection.count_documents({}) > 0:
        recommend_collection.delete_many({}) 
        
    recommend_collection.insert_many(songs)

    
if __name__ == "__main__":
    addRecommendations()
    
    app.run(host="0.0.0.0", port=5001, debug=True)
