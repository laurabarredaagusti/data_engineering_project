from crypt import methods
from fileinput import filename
from flask import Flask, request, render_template, url_for
import os
import pickle

os.chdir(os.path.dirname(__file__))

app = Flask(__name__, static_folder='static')
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return render_template('index.html')

# 1. Devolver la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/predict', methods=['GET'])
def predict():
    model = pickle.load(open('model_random','rb'))

    country = request.args.get('country', None)
    season = request.args.get('season', None)
    home_team_name = request.args.get('home_team_name', None)
    away_team_name = request.args.get('away_team_name', None)

    le_country = pickle.load(open('le_country','rb'))
    le_season = pickle.load(open('le_season','rb'))
    le_home_team_name = pickle.load(open('le_home_team_name','rb'))
    le_away_team_name = pickle.load(open('le_away_team_name','rb'))

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

    # if league_id is None or season is None or home_team_name or away_team_name is None:
    #     return league_id + ' ' + season + ' ' + home_team_name + ' ' + away_team_name
    # else:
    #     prediction = model.predict([[league_id,season,home_team_name,away_team_name]])
    #     return "Prediction: " + str(prediction)

app.run()