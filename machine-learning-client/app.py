from pymongo import MongoClient
import numpy as np
import time

import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import torchaudio
# from transformers import AutoConfig, Wav2Vec2FeatureExtractor

# import librosa
# import IPython.display as ipd
# import numpy as np
# import pandas as pd
# Use a pipeline as a high-level helper
from transformers import pipeline

'''
pipe = pipeline("audio-classification", model="leo-kwan/wav2vec2-base-100k-gtzan-music-genres-finetuned-gtzan")
pipe.save_pretrained("model")
'''

'''
pipe2 = pipeline("audio-classification", model="SavorSauce/music_genres_classification-finetuned-gtzan")
pipe2.save_pretrained("model2")
'''

'''
pipe = pipeline("audio-classification", model="model2")
result = pipe("3_symphony_short.mp3")
print(result)
'''

pipe = pipeline("audio-classification", model="leo-kwan/wav2vec2-base-100k-gtzan-music-genres-finetuned-gtzan")
pipe.save_pretrained("model")

pipe = pipeline("audio-classification", model="model")
result = pipe("3_symphony_short.mp3")
print(result)


# result = pipe("3_symphony.mp3")
# print(result)


'''
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name_or_path = "m3hrdadfi/wav2vec2-base-100k-voxpopuli-gtzan-music"
config = AutoConfig.from_pretrained(model_name_or_path)
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name_or_path)
sampling_rate = feature_extractor.sampling_rate
model = Wav2Vec2ForSpeechClassification.from_pretrained(model_name_or_path).to(device)


def speech_file_to_array_fn(path, sampling_rate):
    speech_array, _sampling_rate = torchaudio.load(path)
    resampler = torchaudio.transforms.Resample(_sampling_rate)
    speech = resampler(speech_array).squeeze().numpy()
    return speech


def predict(path, sampling_rate):
    speech = speech_file_to_array_fn(path, sampling_rate)
    inputs = feature_extractor(speech, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    inputs = {key: inputs[key].to(device) for key in inputs}

    with torch.no_grad():
        logits = model(**inputs).logits

    scores = F.softmax(logits, dim=1).detach().cpu().numpy()[0]
    outputs = [{"Label": config.id2label[i], "Score": f"{round(score * 100, 3):.1f}%"} for i, score in enumerate(scores)]
    return outputs


path = "./3_symphony.mp3"
outputs = predict(path, sampling_rate)
'''



'''
# from modelscope import snapshot_download
from modelscope.models import Model
from modelscope.pipelines import pipeline

model_dir = './save.pt'
model = Model.from_pretrained(model_dir)

inference_pipeline = pipeline('music-genre-classification', model=model)

result = inference_pipeline("./3_symphony.mp3")

print(result)


# model_dir = snapshot_download('ccmusic-database/music_genre')
'''

'''
def collect_and_analyze_data():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client.ml_data
    collection = db.results

    while True:
        data = {"values": list(np.random.rand(5))}
        collection.insert_one(data)
        print("Data inserted:", data)
        time.sleep(10) 

if __name__ == "__main__":
    collect_and_analyze_data()
'''
