import pickle
from flask import request
import sqlite3
import pandas as pd
from datetime import datetime

def get_arguments(arg):
    feature = request.args.get(arg, None)
    return feature

def load_models(model_name):
    path = '../../big_files/' + model_name
    model = pickle.load(open(path,'rb'))
    return model

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
    crsr.execute(query, params)
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
