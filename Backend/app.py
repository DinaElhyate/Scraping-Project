from flask import Flask, jsonify
import csv
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Fonction pour lire les données du fichier CSV
def read_data_from_csv(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

@app.route('/api/data', methods=['GET'])
def get_data():
    data = read_data_from_csv('data.csv')
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
