from flask import Flask, request, json
import librosa 
import librosa.display
import matplotlib
matplotlib.use('PS')
import numpy, scipy, matplotlib.pyplot as plt, librosa, sklearn

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
import urllib.request


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

@app.route('/classify/<path:sound_url>', methods=['GET'])
def classify(sound_url):

    sound_name = sound_url.split('/')[-1]
    file_name = 'Download/' + sound_name
    with urllib.request.urlopen(sound_url) as response:
        with open(file_name, 'wb') as out_file:
           data = response.read() 
           out_file.write(data)
    print(file_name)

    y, fs = librosa.load(file_name,sr=None,mono=True)
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
    print(label)
    label = "{}: {:.2f}%".format(label, proba[idx] * 100)
    identification = "[INFO] {}".format(label)
    #print("[INFO] {}".format(label))
    print(identification)
    K.clear_session()

    return identification

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

@app.route('/download/<path:some_url>', methods = ['GET'])
def download(some_url):
    print(some_url)
    file_name = some_url.split('/')[-1]
    file_name = 'Download/' + file_name
    with urllib.request.urlopen(some_url) as response:
        with open(file_name, 'wb') as out_file:
           data = response.read() 
           out_file.write(data)
    return file_name

    
if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0')
