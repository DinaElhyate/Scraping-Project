from flask import Flask, jsonify
from flask_socketio import SocketIO
import csv
import os
import time
from flask_cors import CORS
import threading
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Initialiser l'application Flask et SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Chemin du fichier CSV
csv_filename = 'dataVersion2.csv'

# URL de la page à analyser
url = "https://fr.investing.com/commodities/crude-oil-commentary"

# Fonction pour lire les données du fichier CSV

def read_data_from_csv(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row = {k: (v if v is not None else '') for k, v in row.items()}
                data.append(row)
    return data
# Fonction pour extraire les commentaires
def extract_comments(driver):
    comments = []
    try:
        # Exemple d'extraction des commentaires depuis la page (selon la structure HTML)
        comment_elements = driver.find_elements(By.CSS_SELECTOR, '.js-comment-body')  # Modifier selon l'élément réel des commentaires
        for element in comment_elements:
            comments.append(element.text)
    except Exception as e:
        print(f"Erreur lors de l'extraction des commentaires : {e}")
    return comments

# Fonction pour analyser le sentiment d'un commentaire (simple exemple)
def analyze_sentiment(comment):
    if "augmentation" in comment.lower():
        return "Positif"
    elif "préoccupante" in comment.lower():
        return "Négatif"
    else:
        return "Neutre"

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
    
    # Démarrer l'application Flask avec SocketIO
     socketio.run(app, debug=True, port=5001)
