from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

@app.route("/")
def index():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client.ml_data
    results = db.results.find()

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
