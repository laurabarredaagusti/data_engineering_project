from flask import Flask, request, jsonify
import os

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return "Welcome to the soccer game predictor."

app.run()