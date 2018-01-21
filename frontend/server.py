"""
    Front-end server for deepmersion.
"""
import os
import sys
import requests
import numpy as np

from PIL import Image
from flask import Flask, request, send_from_directory, send_file, jsonify

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.bridge import Bridge
from vision_vgg_objects import classify_objects
from run_placesCNN_unified import *

bridge = Bridge(path_to_db='../backend/db/')

app = Flask(__name__, static_folder='deepmersion/build/static', static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# serve static files produced by react
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('deepmersion/build/static', path)

@app.route('/sounds/<path:path>')
def send_sounds(path):
    return send_from_directory('deepmersion/build/sounds', path)

@app.route('/')
def send_home():
    return send_file('deepmersion/build/index.html')

def do_classification(image):
    places_prob, weight_softmax, idx = classify_places(image)
    objects_prob = classify_objects(image)
    #return objects_prob, places_prob
    return -6 * np.random.random((1000,)), -6 * np.random.random((401,))

@app.route('/classify', methods=['POST'])
def classify():
    if not 'image' in request.files:
        if 'image_url' in request.form:
            image = requests.get(request.form['image_url'], stream=True).raw
    else:
        image = request.files['image']
    
    # do the stuff here
    obj_dist, plc_dist = do_classification(image)
    volumes = bridge.get_sound(obj_dist, plc_dist, float(request.form['chatterLevel']), request.form['useObjects'], request.form['usePlaces'], request.form['useChatter'])

    return jsonify({ 'volumes': list(volumes), 'objectTags': ['a', 'b', 'c'], 'placeTags': ['d', 'e', 'f']})

if __name__ == '__main__':
    app.run(debug=True)

