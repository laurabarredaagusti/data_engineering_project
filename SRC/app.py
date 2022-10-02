from crypt import methods
from fileinput import filename
from flask import Flask, request, render_template, url_for
import os
import pickle
import sqlite3

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

    country = request.args.get('country', None)
    season = request.args.get('season', None)
    home_team_name = request.args.get('home_team_name', None)
    away_team_name = request.args.get('away_team_name', None)

    if country is None or season is None or home_team_name is None or away_team_name is None:
        return 'Not enough arguments'
    else:
        le_country = pickle.load(open('../../big_files/le_country','rb'))
        le_season = pickle.load(open('../../big_files/le_season','rb'))
        le_home_team_name = pickle.load(open('../../big_files/le_home_team_name','rb'))
        le_away_team_name = pickle.load(open('../../big_files/le_away_team_name','rb'))

        country = le_country.transform([country])
        season = le_season.transform([season])
        home_team_name = le_home_team_name.transform([home_team_name])
        away_team_name = le_away_team_name.transform([away_team_name])

        country = country[0]
        season = season[0]
        home_team_name = home_team_name[0]
        away_team_name = away_team_name[0]

        prediction = model.predict([[country, season, home_team_name, away_team_name]])
        prediction =  str(prediction[0])
        
        return render_template('predict.html', predict=prediction)

# 1. Devolver la predicción de los nuevos datos enviados mediante argumentos en la llamada
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

    return 'Data has been added to the database'

app.run()