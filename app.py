from flask import Flask, request, json
import librosa 
import librosa.display
import matplotlib
matplotlib.use('PS')
import numpy, scipy, matplotlib.pyplot as plt, librosa, sklearn
# import urllib.request

from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import argparse
import imutils
import pickle
import cv2
import os
import boto3
import botocore
from keras import backend as K


BUCKET_NAME = 'testingsoundsbirds'
KEY = 'andropadusAWS.mp3'

modelName = 'it_5.model'
labelName = 'lb.pickle'


def save_image(picName):
    plt.savefig(picName, bbox_inches='tight', pad_inches=0)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Mo Salah'

@app.route('/classify/<sound_url>', methods=['GET'])
def classify(sound_url):
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY, 'local_sound.mp3')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    y, fs = librosa.load('local_sound.mp3',sr=None,mono=True)
    message = "MFCC was generated!"
    mfccs = librosa.feature.mfcc(y, sr=fs, n_fft=1024, hop_length=512, n_mfcc=13, fmin=0,fmax=8000)
    mfccs = sklearn.preprocessing.scale(mfccs, axis=1)  
    librosa.display.specshow(mfccs, sr=fs*2, cmap='coolwarm')
    imageName = 'test.png'
    save_image(imageName)
    image = cv2.imread(imageName)
    output = image.copy()

    image = cv2.resize(image, (200, 100))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    

    print("[INFO] loading network...")
    model = load_model(modelName)
    lb = pickle.loads(open(labelName, "rb").read())

    print("[INFO] classifying image...")
    proba = model.predict(image)[0]
    idx = np.argmax(proba)
    label = lb.classes_[idx]
    filename = imageName[imageName.rfind(os.path.sep) + 1:]
    label = "{}: {:.2f}%".format(label, proba[idx] * 100)
    print("[INFO] {}".format(label))
    K.clear_session()

    return sound_url

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/keita', methods = ['POST'])
def api_message():

    if request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0')