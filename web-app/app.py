"""
This module implements a Flask-based web application for a music genre detector.
It uses a pretrained music genre classification model called music_genre 
to detect the genre of the input music and categorizes music into the following categories:
['blues','classical', 'country','disco','hiphop','jazz','metal','pop','reggae','rock']
Link to the model: https://huggingface.co/ccmusic-database/music_genre
The application allows uploading a mp3 or wav file, as well as recording via microphone. 
The application keeps track of your most recent uploads, statistics on each genre 
and a recommendation list generated based on the statistics

Author:
- Thomas Chen, An Hai, Annabella Lee, Edison Wang
"""


import secrets
import ast

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId


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
    """
    Renders the home page for the logged-in user.

    This function fetches the current user's genre statistics and song recommendations 
    based on their preferences. 

    Returns:
        flask.Response: The rendered 'home.html' template with:
            - genres: A list of dictionaries containing genre statistics, including:
                - "Name": The genre name.
                - "Amount": The count of songs in the genre.
                - "Percentage": The percentage of songs in the genre.
            - recommendations: A list of dictionaries containing song recommendations, including:
                - "Title": The song title.
                - "Artist": The artist's name.
                - "Genre": The genre of the song.

    Raises:
        RuntimeError: If the user is not logged in(@login_required decorator)
    """
    cur_user = current_user.username
    cur_user_collection = db[cur_user]
    genres = get_stats(cur_user_collection)
    recommendations = get_recommendations(genres)
    return render_template('home.html', genres = genres, recommendations = recommendations)

def get_stats(cur_user_collection):
    """
    Computes the genre statistics for a user's song collection.

    Args:
        cur_user_collection: The MongoDB collection corresponding to the current user, 
        containing their song data.

    Returns:
        list: A list of dictionaries, where each dictionary represents a genre and contains:
            - "Name" (str): The genre name.
            - "Amount" (int): The count of songs in this genre.
            - "Percentage" (str): The percentage of songs in this genre, formatted as a string 
              with two decimal places.
    """
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

def get_recommendations(genres):
    """
    Generates song recommendations based on the user's top genres.

    Args:
        genres (list): A list of dictionaries, where each dictionary represents 
            a genre and contains:
            - "Name" (str): The genre name.
            - "Amount" (int): The count of songs in this genre.

    Returns:
        list: A list of dictionaries, where each dictionary represents a recommended song:
            - "Title" (str): The title of the song.
            - "Artist" (str): The artist of the song.
            - "Genre" (str): The genre of the song.

    Raises:
        KeyError: If the "Name" or "Amount" keys are missing in the input genres list.
        ValueError: If the input genres list is not valid or empty.
    sorted_genres = sorted(genres, key=lambda x: x["Amount"], reverse=True)
    """
    sorted_genres = sorted(genres, key=lambda x: x["Amount"], reverse=True)

    if len(sorted_genres) == 0:
        return []

    top_genre = sorted_genres[0]
    second_genre = sorted_genres[1] if len(sorted_genres) > 1 else None

    total_amount = top_genre["Amount"] + (second_genre["Amount"] if second_genre else 0)
    top_genre_count = round(5 * (top_genre["Amount"] / total_amount))
    second_genre_count = 5 - top_genre_count

    recommend_collection = db["recommendations"]

    top_genre_songs = list(
        recommend_collection.aggregate([
            {"$match": {"genre": top_genre["Name"]}},
            {"$sample": {"size": top_genre_count}}
        ])
    )
    second_genre_songs = []
    if second_genre:
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
    """
    Reads the contents of 'songs.txt', parses the data, 
    and populates the MongoDB 'recommendations' collection.

    Returns: 
        None

    Raises:
        FileNotFoundError: If the 'songs.txt' file is not found.
        ValueError: If the content of 'songs.txt' cannot be parsed as a valid Python list.
        pymongo.errors.PyMongoError: If there are issues with MongoDB operations.
    """
    recommend_collection = db.recommendations

    with open("songs.txt", "r", encoding="utf-8") as f:
        file_content = f.read()

    songs_dict = ast.literal_eval(file_content)
    songs = songs_dict if isinstance(songs_dict, list) else []


    if recommend_collection.count_documents({}) > 0:
        recommend_collection.delete_many({})

    recommend_collection.insert_many(songs)


@app.route('/upload', methods=['POST'])
def upload():
    music_name = request.form.get('music_name')
    author = request.form.get('author')
    music_file = request.files.get('music_file')
    recorded_audio = request.form.get('recorded_audio')

    if music_file:
        music_file.save(f'uploads/{music_name}_{author}.mp3')
    elif recorded_audio:
        import base64
        audio_data = base64.b64decode(recorded_audio.split(',')[1])
        with open(f'uploads/{music_name}_{author}.webm', 'wb') as f:
            f.write(audio_data)

    return "Upload successful"




if __name__ == "__main__":
    addRecommendations()
    app.run(host="0.0.0.0", port=5001, debug=True)
