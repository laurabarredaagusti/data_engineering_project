import pickle
from flask import Flask, request, render_template, url_for

def get_arguments(arg):
    feature = request.args.get(arg, None)
    return feature

def load_models(model_name):
    path = '../../big_files/' + model_name
    model = pickle.load(open(path,'rb'))
    return model

def encode(model, feature):
    encoded_feature = model.transform([feature])
    encoded_feature = encoded_feature[0]
    return encoded_feature

def get_prediction(model, feature_list):
    prediction = model.predict([feature_list])
    prediction = str(prediction[0])
    return prediction

