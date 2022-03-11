
import flask
from flask import Flask, jsonify, request, render_template
import json
import numpy as np
import pickle


app = Flask(__name__)

#define a function to load our pickled model
def load_models():
    file_name = "models/model_file.p"
    with open(file_name, 'rb') as pickled:
        data = pickle.load(pickled)
        model = data['model']
    return model


#api endpoint for our root html page
@app.route("/")

def index():
    return render_template("index.html")

#our api endpoint that takes in fetures and makes prediction
@app.route('/predict', methods=['GET', 'POST'])

#define our predict function "endpoint" that predicts our price based on features
def predict():

    # parse input features from request
    
    request_json = request.get_json()

    x = request_json['input']

    x_in=np.array(x).reshape(1,-1)
    #load model
    model = load_models()
    prediction = model.predict(x_in)[0]
    response = json.dumps({'response': prediction})
    print(prediction)
    return response, 200


    '''
    response = json.dumps({'response': 'yahhhh!'})
    return response, 200
    '''
if __name__ == '__main__':
    application.run(debug=True)
