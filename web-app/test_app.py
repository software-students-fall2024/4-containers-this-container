"""
Unit Tests for the Flask-based web application in `app.py`.

This module tests various functionalities of the web application, including:
- User registration, login, and session handling.
- Genre statistics and song recommendations.
- Adding recommendations from a `songs.txt` file to the database.
- Route behavior for logged-in and logged-out states.

Author:
- Thomas Chen, An Hai, Annabella Lee, Edison Wang
"""
# pylint: disable=redefined-outer-name
import ast
from unittest.mock import patch, MagicMock, mock_open
import pytest
from bson.objectid import ObjectId
from app import app, get_stats, get_recommendations, add_recommendations


SONGS_CONTENT = """[
    {"title": "The Thrill is Gone", "artist": "B.B. King", "genre": "Blues"},
    {"title": "Cross Road Blues", "artist": "Robert Johnson", "genre": "Blues"}
]"""

@pytest.fixture
def flask_client():
    """
    Provide a Flask test client for testing application routes.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("app.db")
def test_get_stats(mock_db):
    """
    Test the `get_stats` function for calculating genre statistics.
    """
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = [
        {"_id": "rock", "count": 5},
        {"_id": "pop", "count": 3},
    ]
    mock_db.return_value = mock_collection

    stats = get_stats(mock_collection)
    expected_stats = [
        {"Name": "rock", "Amount": 5, "Percentage": "62.50%"},
        {"Name": "pop", "Amount": 3, "Percentage": "37.50%"},
    ]

    assert stats == expected_stats
    mock_collection.aggregate.assert_called_once()

@patch("app.db")
def test_get_recommendations(mock_db):
    """
    Test the `get_recommendations` function for generating song recommendations.
    """
    mock_recommendations = MagicMock()
    mock_db.recommendations = mock_recommendations
    mock_recommendations.aggregate.side_effect = [
        [
            {"title": "Song A", "artist": "Artist 1", "genre": "rock"},
            {"title": "Song C", "artist": "Artist 3", "genre": "rock"},
            {"title": "Song D", "artist": "Artist 4", "genre": "rock"},
        ],
        [
            {"title": "Song B", "artist": "Artist 2", "genre": "pop"},
            {"title": "Song E", "artist": "Artist 5", "genre": "pop"},
        ],
    ]

    genres = [{"Name": "rock", "Amount": 5}, {"Name": "pop", "Amount": 3}]

    recommendations = get_recommendations(genres)

    expected_recommendations = [
        {"Title": "Song A", "Artist": "Artist 1", "Genre": "rock"},
        {"Title": "Song C", "Artist": "Artist 3", "Genre": "rock"},
        {"Title": "Song D", "Artist": "Artist 4", "Genre": "rock"},
        {"Title": "Song B", "Artist": "Artist 2", "Genre": "pop"},
        {"Title": "Song E", "Artist": "Artist 5", "Genre": "pop"},
    ]

    assert mock_recommendations.aggregate.call_count == 2
    assert recommendations == expected_recommendations




def test_home_route_logged_out(flask_client):
    """
    Test accessing the home route without being logged in.
    """
    response = flask_client.get("/home", follow_redirects=True)
    assert response.status_code == 200
    assert b'<form' in response.data
    assert b'Register' in response.data

@patch("app.get_stats")
@patch("app.get_recommendations")
@patch("flask_login.utils._get_user")
def test_home_route_logged_in(
    mock_get_user,
    mock_get_recommendations,
    mock_get_stats,
    flask_client
): 
    """
    Test the home route when a user is logged in.
    """
    mock_get_user.return_value.is_authenticated = True
    mock_get_user.return_value.username = "test_user"
    mock_get_stats.return_value = [
        {"Name": "rock", "Amount": 5, "Percentage": "62.50%"},
    ]
    mock_get_recommendations.return_value = [
        {"Title": "Song A", "Artist": "Artist 1", "Genre": "rock"},
    ]

    response = flask_client.get("/home")
    assert response.status_code == 200
    assert b"rock" in response.data
    assert b"Song A" in response.data

@patch("app.db.create_collection")
@patch("app.users_collection.find_one")
@patch("app.generate_password_hash")
def test_register_success(
    mock_generate_password_hash,
    mock_find_one,
    mock_create_collection,
    flask_client
):
    """
    Test the registration process with valid data.
    """
    mock_find_one.return_value = None
    mock_generate_password_hash.return_value = "hashed_password"

    response = flask_client.post(
        "/register",
        data={"username": "new_user", "password1": "password", "password2": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful!" in response.data
    
    mock_create_collection.assert_called_once_with("new_user")

def test_register_password_mismatch(flask_client):
    """
    Test the registration process when passwords do not match.
    """
    response = flask_client.post(
        "/register",
        data={"username": "new_user", "password1": "password", "password2": "pass"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

@patch("app.users_collection.find_one")
def test_login_invalid_credentials(mock_find_one, flask_client):
    """
    Test the login process with invalid credentials.
    """
    mock_find_one.return_value = None

    response = flask_client.post(
        "/login",
        data={"username": "test_user", "password": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

@patch("app.users_collection.find_one")
@patch("app.check_password_hash")
def test_login_success(mock_check_password_hash, mock_find_one, flask_client):
    """
    Test the login process with valid credentials.
    """
    mock_find_one.return_value = {"_id": ObjectId(), "username": "test_user", "password": "hashed"}
    mock_check_password_hash.return_value = True

    response = flask_client.post(
        "/login",
        data={"username": "test_user", "password": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

@patch("app.db")
@patch("builtins.open", new_callable=mock_open, read_data=SONGS_CONTENT)
def test_add_recommendations(mock_file, mock_db):
    """
    Test the `add_recommendations` function by reading `songs.txt` and verifying
    that the data is correctly added to the mock database.
    """
    mock_recommendations = MagicMock()
    mock_db.recommendations = mock_recommendations

    mock_recommendations.count_documents.return_value = 5

    add_recommendations()

    expected_songs = ast.literal_eval(SONGS_CONTENT)

    mock_file.assert_called_once_with("songs.txt", "r", encoding="utf-8")

    mock_recommendations.delete_many.assert_called_once_with({})
    mock_recommendations.insert_many.assert_called_once_with(expected_songs)
