from crypt import methods
from fileinput import filename
from flask import Flask, request, render_template, url_for
import os
import pickle
import sqlite3
import pandas as pd
from sklearn import metrics
import json
from datetime import datetime
from functions import *

os.chdir(os.path.dirname(__file__))

app = Flask(__name__, static_folder='static')
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return render_template('index.html')


# 1. Devolver la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/predict', methods=['GET'])
def predict():
    model = pickle.load(open('../../big_files/model_random','rb'))

    country = get_arguments('country')
    season = get_arguments('season')
    home_team_name = get_arguments('home_team_name')
    away_team_name = get_arguments('away_team_name')

    if country is None or season is None or home_team_name is None or away_team_name is None:
        return 'Not enough arguments'
    else:
        le_country = load_models('le_country')
        le_season = load_models('le_season')
        le_home_team_name = load_models('le_home_team_name')
        le_away_team_name = load_models('le_away_team_name')

        country = encode(le_country, country)
        season = encode(le_season, season)
        home_team_name = encode(le_home_team_name, home_team_name)
        away_team_name = encode(le_away_team_name, away_team_name)

        feature_list = [country, season, home_team_name, away_team_name]

        prediction = get_prediction(model, feature_list)
        
        return render_template('predict.html', predict=prediction)


# 2. Ingestar nuevos datos
@app.route('/ingest', methods=['GET'])
def ingest():
    country = request.args.get('country', None)
    season = request.args.get('season', None)
    home_team_name = request.args.get('home_team_name', None)
    away_team_name = request.args.get('away_team_name', None)
    result = request.args.get('result', None)

    params = (country, season, home_team_name, away_team_name, result)

    connection = sqlite3.connect("database.sqlite")
    crsr = connection.cursor()

    query = '''INSERT INTO prediction VALUES (?,?,?,?,?);'''

    crsr.execute(query, params)

    connection.close()

    return 'Data has been added to the database'


# 3. Monitorizar rendimiento
@app.route('/monitor', methods=['GET'])
def monitor():
    model = pickle.load(open('../../big_files/model_random','rb'))
    le_country = pickle.load(open('../../big_files/le_country','rb'))
    le_season = pickle.load(open('../../big_files/le_season','rb'))
    le_home_team_name = pickle.load(open('../../big_files/le_home_team_name','rb'))
    le_away_team_name = pickle.load(open('../../big_files/le_away_team_name','rb'))

    connection = sqlite3.connect("../../big_files/database.sqlite")
    crsr = connection.cursor()

    query = '''SELECT * FROM prediction'''

    crsr.execute(query)
    ans = crsr.fetchall()
    names = [description[0] for description in crsr.description]

    df = pd.DataFrame(ans,columns=names)

    df['country'] = le_country.transform(df['country'])
    df['season'] = le_season.transform(df['season'])
    df['home_team_name'] = le_home_team_name.transform(df['home_team_name'])
    df['away_team_name'] = le_away_team_name.transform(df['away_team_name'])

    connection.close()

    X = df.drop('result', axis=1)
    y = df['result']

    prediction = model.predict(X)

    new_accuracy = metrics.accuracy_score(y, prediction)

    f = open('accuracy_monitor.json')
    dict = json.load(f)
    accuracy = dict['accuracy_0']

    if new_accuracy < accuracy:
        return 'The accuracy is not improving, the model needs to be retrained'
    else:
        return 'The model does not need to be retrained'


# 4. Reentrenar modelo
@app.route('/retrain', methods=['GET'])
def retrain():
    model = pickle.load(open('../../big_files/model_random','rb'))
    le_country = pickle.load(open('../../big_files/le_country','rb'))
    le_season = pickle.load(open('../../big_files/le_season','rb'))
    le_home_team_name = pickle.load(open('../../big_files/le_home_team_name','rb'))
    le_away_team_name = pickle.load(open('../../big_files/le_away_team_name','rb'))

    connection = sqlite3.connect("../../big_files/database.sqlite")
    crsr = connection.cursor()    

    query = '''SELECT * FROM prediction'''

    crsr.execute(query)
    ans = crsr.fetchall()
    names = [description[0] for description in crsr.description]

    df = pd.DataFrame(ans,columns=names)

    df['country'] = le_country.transform(df['country'])
    df['season'] = le_season.transform(df['season'])
    df['home_team_name'] = le_home_team_name.transform(df['home_team_name'])
    df['away_team_name'] = le_away_team_name.transform(df['away_team_name'])

    connection.close()

    X = df.drop('result', axis=1)
    y = df['result']

    model.fit(X,y)

    date = str(datetime.today().strftime('%y%m%d%H%M%S'))
    name = 'model_random' + date
    path = '../../big_files/' + name
    pickle.dump(model, open(path,'wb'))

    result = "New model retrained and saved as " + name

    return result

app.run()