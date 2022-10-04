import pickle
from flask import request
import sqlite3
import pandas as pd
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import Flask
import json

def app_config():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['UPLOAD_FOLDER'] = 'static/files'
    return app

def get_arguments(arg):
    return request.args.get(arg, None)

def load_models(model_name):
    path = '../../big_files/' + model_name
    return pickle.load(open(path,'rb'))

def encode(model, feature):
    encoded_feature = model.transform(feature)
    encoded_feature = encoded_feature[0]
    return encoded_feature

def get_prediction(model, feature_list):
    prediction = model.predict([feature_list])
    prediction = str(prediction[0])
    return prediction

def insert_data_sql(params):
    query = '''INSERT INTO prediction VALUES (?,?,?,?,?);'''
    path = '../../big_files/database.sqlite'
    connection = sqlite3.connect(path)
    crsr = connection.cursor()
    crsr.executemany(query, params)
    connection.commit()
    connection.close()

def df_from_sql():
    query = '''SELECT * FROM prediction'''
    path = '../../big_files/database.sqlite'
    connection = sqlite3.connect(path)
    crsr = connection.cursor()
    crsr.execute(query)
    ans = crsr.fetchall()
    names = [description[0] for description in crsr.description]
    df = pd.DataFrame(ans,columns=names)
    connection.close()
    return df

def save_model(model):
    date = str(datetime.today().strftime('%y%m%d%H%M%S'))
    name = 'model_random' + date
    path = '../../big_files/' + name
    pickle.dump(model, open(path,'wb'))

def save_file(form,app):
    file = form.file.data 
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))
    file.save(path)

def df_from_json(path):
    with open(path, 'r') as f:
        data = json.loads(f.read())
        return pd.json_normalize(data)
