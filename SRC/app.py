from flask import Flask, request, jsonify
import os
import pickle

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return "Welcome to the soccer game predictor."

# 1. Devolver la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/predict', methods=['GET'])
def predict():
    model = pickle.load(open('model/model_random','rb'))

    league_id = int(request.args.get('league_id', None))
    season = int(request.args.get('season', None))
    home_team_name = int(request.args.get('home_team_name', None))
    away_team_name = int(request.args.get('away_team_name', None))

    prediction = model.predict([[league_id,season,home_team_name,away_team_name]])
    return "Prediction: " + str(prediction)

    # if league_id is None or season is None or home_team_name or away_team_name is None:
    #     return league_id + ' ' + season + ' ' + home_team_name + ' ' + away_team_name
    # else:
    #     prediction = model.predict([[league_id,season,home_team_name,away_team_name]])
    #     return "Prediction: " + str(prediction)

app.run()