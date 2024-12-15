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

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

csv_filename = 'dataVersion2.csv'

url = "https://fr.investing.com/commodities/crude-oil-commentary"


def read_data_from_csv(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row = {k: (v if v is not None else '') for k, v in row.items()}
                data.append(row)
    return data
def extract_comments(driver):
    comments = []
    try:
        comment_elements = driver.find_elements(By.CSS_SELECTOR, '.js-comment-body')  
        for element in comment_elements:
            comments.append(element.text)
    except Exception as e:
        print(f"Erreur lors de l'extraction des commentaires : {e}")
    return comments

def analyze_sentiment(comment):
    if "augmentation" in comment.lower():
        return "Positif"
    elif "préoccupante" in comment.lower():
        return "Négatif"
    else:
        return "Neutre"

def monitor_csv():
    last_update_time = os.path.getmtime(csv_filename) if os.path.exists(csv_filename) else None
    while True:
        time.sleep(1)  
        if os.path.exists(csv_filename):
            current_update_time = os.path.getmtime(csv_filename)
            if current_update_time != last_update_time:
                last_update_time = current_update_time
                data = read_data_from_csv(csv_filename)
                socketio.emit('update', data)  


@app.route('/api/data', methods=['GET'])
def get_data():
    data = read_data_from_csv(csv_filename)
    return jsonify(data)

if __name__ == '__main__':

     thread = threading.Thread(target=monitor_csv)
     thread.start()
    

     socketio.run(app, debug=True, port=5001)
