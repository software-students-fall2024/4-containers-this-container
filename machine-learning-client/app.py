"""
This module downloads a pretrained music genre classification model.
Once downloaded, the model can be reused locally to perform inferences.
This module includes functions to download or load the model, make inferences 
with the model, and parse the inference result and output the model's prediction.
"""

import base64
# from pymongo import MongoClient
from transformers import pipeline
from flask import Flask, request, jsonify
from pydub import AudioSegment

app = Flask(__name__)

def download_model():
    """
    Download model from online. The model data will be stored in a
    directory named "model" in the same directory as this file.

    Returns:
        None
    """
    pipe = pipeline(
        "audio-classification",
        model="leo-kwan/wav2vec2-base-100k-gtzan-music-genres-finetuned-gtzan",
    )
    pipe.save_pretrained("model")


def inference(audio_file):
    """
    Make inference on an audio file with the model.

    Args:
        audio_file (str): Path to the audio file.

    Returns:
        result: An array of dictionaries, each of which contains a label field and a score field.
    """
    pipe = pipeline("audio-classification", model="model")
    result = pipe(audio_file)
    return result


def parse_result(result):
    """
    Parse the result returned by inference() to get the top 1 prediction from the model.

    Args:
        result (array): An array of dictionaries returned by calling inference().

    Returns:
        prediction: A string that is the best prediction of the music genre.
    """
    max_prob = 0
    prediction = "We don't know what the type of this music is :("
    for category in result:
        if category["score"] >= max_prob:
            prediction = category["label"]
            max_prob = category["score"]
    return prediction


def predict(audio_data):
    """
    Main function to download or load the model, make an inference, and parse and return the result.

    Args:
        audio_data (str): raw audio data.
        
    Returns:
        pred: prediction of the model.
    """
    download_model()
    audio_segment = AudioSegment(
        audio_data,
        frame_rate=16000,  # Sampling rate
        sample_width=2,    # 2 bytes = 16-bit audio
        channels=1         # Mono audio
    )

    # Export the audio to an MP3 file
    output_file = "output.mp3"
    audio_segment.export(output_file, format="mp3")
    result = inference(output_file)
    pred = parse_result(result)
    # print(f"The genre of your music is: {pred}.")
    return pred


# main("3_symphony_short.mp3")

@app.route("/classify", methods=["POST"])
def classify_api():
    """
    ML API that classifies the music.
    
    Returns:
        result: classification result.
    """
    audio_json = request.get_json()
    audio_data = audio_json.get("audio")
    raw_audio = base64.b64decode(audio_data.split(",")[1])
    result = predict(raw_audio)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
