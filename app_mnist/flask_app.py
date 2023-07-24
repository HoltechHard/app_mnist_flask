# import packages
from flask import Flask, request, render_template, jsonify
import numpy as np
from keras.models import model_from_json
import tensorflow as tf
from PIL import Image
import os
from werkzeug.utils import secure_filename
import sqlite3

# read the json file which contains the model
json_file = open("model_api/model.json", "r")
model_json = json_file.read()
json_file.close()

# load the parameters of the model
model = model_from_json(model_json)
model.load_weights("model_api/weights.h5")
model.compile(loss = "categorical_crossentropy", optimizer = "adam",
              metrics = ["accuracy"])
graph = tf.compat.v1.get_default_graph()

# get the list of image paths
def get_image_paths():
    image_dir = 'static/images'
    image_paths = [os.path.join(image_dir, filename) for filename in os.listdir(image_dir)]
    return image_paths

# save register of image path and prediction in database
def insert_register(img_path, pred):
    # connect with sqlite
    cnn = sqlite3.connect('mymnist.db')
    # create cursor 
    cursor = cnn.cursor()
    # execute insert
    cursor.execute("insert into tbl_mnist(img_path, pred_class) values(?, ?)",
                (img_path, pred))
    # commit transaction
    cnn.commit()
    # close connection
    cursor.close()
    cnn.close()

    return jsonify({'success': True})

# setting the app
app = Flask(__name__)

# main page
@app.route("/")
def index():
    # load the table with data

    # select database operation
    # connect with sqllite
    cnn = sqlite3.connect('mymnist.db')
    # create cursor
    cursor = cnn.cursor()
    # query to read the last inserted data
    cursor.execute("select id_image, img_path, pred_class from tbl_mnist")
    # retrieve data
    rows = cursor.fetchall()

    # convert data query to json 
    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'img_path': row[1],
            'pred_class': row[2]
        })
    
    # close connection
    cnn.close()

    return render_template("index.html", data = data)

# convert base64-string to image

import re 
import base64

def stringToImage(img):
    imgstr = re.search(r'base64, (.*)', str(img)).group(1)
    with open('image.png', 'wb') as output:
        output.write(base64.b64decode(imgstr))

# prediction api
@app.route('/predict/', methods = ['POST'])

def predict():
    global model, graph
    img_data = request.get_data()
    try:
        stringToImage(img_data)    
    except:
        f = request.files['image']
        filename = f.filename

    # format the image
    img_path = os.path.join('static/images', filename)
    img = Image.open(img_path)
    img = img.convert('L')
    img_sized = img.resize((28, 28))

    # transform image to use in model
    x = np.asarray(img_sized)
    x = x.reshape((1, 28, 28, 1))

    # make prediction
    prediction = model.predict(x)

    # take class
    response = np.argmax(prediction, axis = 1)

    # insert new register in database
    insert_register(img_path, str(response[0]))

    # object with results    
    return jsonify({
        'class_pred': str(response[0])
    })    

# page to upload image files
@app.route('/upload/', methods = ['GET', 'POST'])
def upload():

    if request.method == 'POST':
        image_file = request.files['image']

        if image_file:
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join('static/images', filename))

        return jsonify({            
            'filename': filename
        })
    
    return 'No image was uploaded'
    
# main call function
if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 80)
    app.run(debug = True)
