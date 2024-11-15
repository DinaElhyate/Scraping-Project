from flask import Flask, jsonify
from flask_socketio import SocketIO
import csv
import os
import time
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Chemin du fichier CSV
csv_filename = 'data.csv'

# Fonction pour lire les données du fichier CSV
def read_data_from_csv(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

# Fonction pour surveiller les mises à jour du fichier CSV
def monitor_csv():
    last_update_time = os.path.getmtime(csv_filename) if os.path.exists(csv_filename) else None
    while True:
        time.sleep(1)  # Vérifie toutes les secondes
        if os.path.exists(csv_filename):
            current_update_time = os.path.getmtime(csv_filename)
            if current_update_time != last_update_time:
                last_update_time = current_update_time
                data = read_data_from_csv(csv_filename)
                socketio.emit('update', data)  # Émettre les données au client

@app.route('/api/data', methods=['GET'])
def get_data():
    data = read_data_from_csv(csv_filename)
    return jsonify(data)

if __name__ == '__main__':
    # Démarrer le thread pour surveiller le fichier CSV
    thread = threading.Thread(target=monitor_csv)
    thread.start()
    
    socketio.run(app, debug=True, port=5000)
