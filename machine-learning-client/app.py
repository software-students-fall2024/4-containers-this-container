"""
This module downloads a pretrained music genre classification model.
Once downloaded, the model can be reused locally to perform inferences.
This module includes functions to download or load the model, make inferences 
with the model, and parse the inference result and output the model's prediction.
"""

# from pymongo import MongoClient
from transformers import pipeline


def download_model():
    """
    Download model from online. The model data will be stored in a
    directory named "model" in the same directory as this file.

    Returns:
        None
    """
    pipe = pipeline("audio-classification", \
                    model="leo-kwan/wav2vec2-base-100k-gtzan-music-genres-finetuned-gtzan")
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


def main(audio_file):
    """
    Main function to download or load the model, make an inference, and parse and print the result.

    Args:
        image_path (str): Path to the input image.
    """
    result = []
    try:
        result = inference(audio_file)
    except Exception as _:
        download_model()
        result = inference(audio_file)
    pred = parse_result(result)
    print(f"The genre of your music is: {pred}.")


main("3_symphony_short.mp3")
