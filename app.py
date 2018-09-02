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

modelName = 'it_5.model'
labelName = 'label.pickle'


def save_image(picName):
    plt.savefig(picName, bbox_inches='tight', pad_inches=0)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Server Operational'

@app.route('/exists/<path:sound_url>', methods=['GET'])
def exists(sound_url):
    sound_name = sound_url.split('/')[-1]
    file_name = 'Download/' + sound_name

    if not os.path.exists(file_name):
        return "false"
    else:
        return "true"




@app.route('/classifyPost', methods=['POST'])
def classifyPost():
    req_data = request.get_json()
    sound_url = req_data['url']
    sound_name = sound_url.split('%')[-1]
    sound_name = sound_name.split('?')[0]
    file_name = sound_name
    if not os.path.exists(file_name):
        with urllib.request.urlopen(sound_url) as response:
            with open(file_name, 'wb') as out_file:
                data = response.read() 
                out_file.write(data)
  

    y, fs = librosa.load(file_name,sr=None,mono=True)
    message = "MFCC was generated!"
    mfccs = librosa.feature.mfcc(y, sr=fs, n_fft=1024, hop_length=512, n_mfcc=13, fmin=0,fmax=8000)
    mfccs = sklearn.preprocessing.scale(mfccs, axis=1)  
    librosa.display.specshow(mfccs, sr=fs*2, cmap='coolwarm')
    imageName = sound_name[:-3] + 'png'
    save_image(imageName)
    image = cv2.imread(imageName)
    output = image.copy()

    image = cv2.resize(image, (200, 100))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    model = load_model(modelName)
    lb = pickle.loads(open(labelName, "rb").read())
    proba = model.predict(image)[0]
    idx = np.argmax(proba)
    label = lb.classes_[idx].decode('ASCII')
    label = "{}: {:.2f}%".format(label, proba[idx] * 100)
    K.clear_session()

    return label



@app.route('/classify/<path:sound_url>', methods=['GET'])
def classify(sound_url):

    sound_name = sound_url.split('/')[-1]
    file_name = 'Download/' + sound_name
    print("name: " + sound_name)
    print("url: " + sound_url)
    if not os.path.exists(file_name):
        with urllib.request.urlopen(sound_url) as response:
            with open(file_name, 'wb') as out_file:
                data = response.read() 
                out_file.write(data)
  

    y, fs = librosa.load(file_name,sr=None,mono=True)
    message = "MFCC was generated!"
    mfccs = librosa.feature.mfcc(y, sr=fs, n_fft=1024, hop_length=512, n_mfcc=13, fmin=0,fmax=8000)
    mfccs = sklearn.preprocessing.scale(mfccs, axis=1)  
    librosa.display.specshow(mfccs, sr=fs*2, cmap='coolwarm')
    imageName = sound_name[:-3] + 'png'
    save_image(imageName)
    image = cv2.imread(imageName)
    output = image.copy()
    image = cv2.resize(image, (200, 100))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    model = load_model(modelName)
    lb = pickle.loads(open(labelName, "rb").read())
    proba = model.predict(image)[0]
    idx = np.argmax(proba)
    label = lb.classes_[idx].decode('ASCII')
    label = "{}: {:.2f}%".format(label, proba[idx] * 100)
    K.clear_session()

    return label
    
if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
