import os
from flask import Flask, request
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from io import BytesIO
from flask_cors import CORS
import requests
from huggingface_hub import hf_hub_download



def prepare_image(img, target_size=(150, 150)):
    img = image.load_img(img, target_size=target_size)  # Load the image with target size
    img_array = image.img_to_array(img)  # Convert the image to a numpy array
    img_array = np.expand_dims(img_array, axis=0)  # Add a batch dimension
    img_array = img_array / 255.0  # Rescale the image to the same range as the training data
    return img_array

MODEL_PATH = "hf/model.h5"
FILENAME = "pneumonia_model.h5"
REPO_ID = "Nishant-1402/Pneumonia"

model_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

# Load the model only once during initialization
pneumonia_model = tf.keras.models.load_model(model_path)

app = Flask(__name__)
CORS(app)


@app.route('/pneumonia', methods=['POST'])
def detect():
    # Get the image from the request
    img = request.files['img']
    
    # Convert the image to a file-like object using BytesIO
    img = BytesIO(img.read())
    
    # Process the image
    img = prepare_image(img)  # Use the image object directly
    
    # Get the model prediction
    prediction = pneumonia_model.predict(img)
    
    # Classify the result based on the prediction
    predicted_class = 'Pneumonia' if prediction > 0.5 else 'Normal'
    
    # Return the classification result
    return predicted_class

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
