from flask import Flask, redirect, render_template, jsonify
import os
from sklearn import metrics
import json
from functions import *
from time import sleep


os.chdir(os.path.dirname(__file__))

app = Flask(__name__, static_folder='static')
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return render_template('index.html')


# 1. Devolver la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/predict', methods=['GET'])
def predict():
    model = load_models('model_random')

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

        country = encode(le_country, [country])
        season = encode(le_season, [season])
        home_team_name = encode(le_home_team_name, [home_team_name])
        away_team_name = encode(le_away_team_name, [away_team_name])

        feature_list = [country, season, home_team_name, away_team_name]

        prediction = get_prediction(model, feature_list)
        
        return render_template('predict.html', predict=prediction)


# 2. Ingestar nuevos datos
@app.route('/ingest', methods=['GET'])
def ingest():
    new_data = get_arguments('new_data')

    # if country is None or season is None or home_team_name is None or away_team_name is None or result is None:
    #     return 'Not enough arguments'
    # else:
    #     params = (country, season, home_team_name, away_team_name, result)
    #     insert_data_sql(params)
    #     return 'Data has been added to the database'
    return 'Data has been added to the database'


# 3. Monitorizar rendimiento
@app.route('/monitor', methods=['GET'])
def monitor():
    model = load_models('model_random')
    le_country = load_models('le_country')
    le_season = load_models('le_season')
    le_home_team_name = load_models('le_home_team_name')
    le_away_team_name = load_models('le_away_team_name')

    df = df_from_sql()

    df['country'] = encode(le_country, df['country'])
    df['season'] = encode(le_season, df['season'])
    df['home_team_name'] = encode(le_home_team_name, df['home_team_name'])
    df['away_team_name'] = encode(le_away_team_name, df['away_team_name'])

    X = df.drop('result', axis=1)
    y = df['result']

    prediction = model.predict(X)

    new_accuracy = metrics.accuracy_score(y, prediction)

    f = open('accuracy_monitor.json')
    dict = json.load(f)
    accuracy = dict['accuracy_0']

    if new_accuracy < accuracy:
        return redirect("/retrain")
    else:
        return 'The model does not need to be retrained'


# 4. Reentrenar modelo
@app.route('/retrain', methods=['GET'])
def retrain():
    model = load_models('model_random')
    le_country = load_models('le_country')
    le_season = load_models('le_season')
    le_home_team_name = load_models('le_home_team_name')
    le_away_team_name = load_models('le_away_team_name')

    df = df_from_sql()

    df['country'] = encode(le_country, df['country'])
    df['season'] = encode(le_season, df['season'])
    df['home_team_name'] = encode(le_home_team_name, df['home_team_name'])
    df['away_team_name'] = encode(le_away_team_name, df['away_team_name'])

    X = df.drop('result', axis=1)
    y = df['result']

    model.fit(X,y)

    save_model(model)

    result = "New model retrained and saved"

    return result


# 4 Comprobar función
@app.route('/print_db', methods=['GET'])
def print_db():

    connection = sqlite3.connect('../../big_files/database.sqlite')
    cursor = connection.cursor()

    query = '''
    SELECT * FROM prediction
    '''

    result = cursor.execute(query).fetchall()
    connection.commit()

    return jsonify(result)

app.run()