from flask import Flask, redirect, render_template, jsonify
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import os
from sklearn import metrics
import json
from functions import *
from time import sleep
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from os import environ

os.chdir(os.path.dirname(__file__))

app = app_config()

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route("/", methods=['GET'])
def hello():
    form = UploadFileForm()
    return render_template('index.html', form=form) 

# 1. Devolver la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/predict', methods=['GET'])
def predict():
    model = load_models('model_random')

    country = get_arguments('country')
    season = get_arguments('season')
    home_team_name = get_arguments('home_team_name')
    away_team_name = get_arguments('away_team_name')

    if country is None or season is None or home_team_name is None or away_team_name is None:
        return render_template('predict_home.html')
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
@app.route('/ingest', methods=['GET','POST'])
def ingest_by_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        save_file(form, app)
        path = 'static/files/new_data.json'
        new_data_df = df_from_json(path)
        lista_valores = new_data_df.values.tolist()
        insert_data_sql(lista_valores)
        return redirect("/monitor")

    return render_template('ingest_home.html', form=form)
    

# 3. Monitorizar rendimiento
@app.route('/monitor', methods=['GET'])
def monitor():
    sleep(2)
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

    f = open('static/monitoring/accuracy_monitor.json')
    dict = json.load(f)
    accuracy = dict['accuracy_0']

    if new_accuracy < accuracy:
        return redirect("/retrain")
    else:
        frase2='The model does not need to be retrained'
        return  render_template('monitor.html', monitor=frase2)


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

    return render_template('retrain.html', retrain=result)


# 4 Comprobar función
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


if __name__ == '__main__':
  app.run(debug = True, host = '0.0.0.0', port=environ.get("PORT", 5000))