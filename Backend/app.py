import numpy as np
import time
from datetime import datetime
import csv
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options 
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.linear_model import LogisticRegression

url = "https://fr.investing.com/commodities/crude-oil-commentary"
csv_filename = 'dataVersion2.csv'

options = Options()
options.binary_location = "/usr/bin/firefox"  # chemin typique sur Ubuntu pour Firefox
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

model = LogisticRegression()

previous_prices = []
data_batch = []

def write_csv_header():
    if os.stat(csv_filename).st_size == 0:
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Prix actuel", "Changement", "Changement (%)", "Heure de mise à jour", "Prédiction du cumul des prix"])

write_csv_header()

try:
    print("Chargement de la page...")
    driver.get(url)

    while True:
        try:
            WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="instrument-price-last"]'))
        )

            price = float(driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-last"]').text.strip().replace(',', ''))
            change = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-change"]').text.strip()
            change_percent = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-change-percent"]').text.strip()
            time_label = driver.find_element(By.CSS_SELECTOR, '[data-test="trading-time-label"]').text.strip()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            previous_prices.append(price)
            if len(previous_prices) > 10:  # Conserver les 10 dernières valeurs
                previous_prices.pop(0)

            if len(previous_prices) == 10:
                X = np.array(previous_prices[:-1]).reshape(-1, 1)
                y = np.array(previous_prices[1:])
                model.fit(X, y)
                predicted_price = model.predict(np.array([[price]]))[0]
            else:
                predicted_price = price  # Pas assez de données pour une prédiction

            data_batch.append([timestamp, price, change, change_percent, time_label, predicted_price])
            
            if len(data_batch) >= 5:
                with open(csv_filename, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(data_batch)
                data_batch.clear()  # Vider le lot après écriture

            print(f"Timestamp: {timestamp}, Prix actuel: {price}, Changement: {change}, Pourcentage: {change_percent}, Heure: {time_label}, Prédiction: {predicted_price}")

            if len(previous_prices) >= 10:
                sma = np.mean(previous_prices[-10:])  # Calcul de la moyenne mobile
                print(f"Moyenne mobile des 10 derniers prix: {sma}")

        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
        
        # Attendre avant la prochaine requête
        time.sleep(10)

except Exception as e:
    print(f"Erreur lors de l'initialisation du pilote : {e}")

finally:
    if 'driver' in locals():
        driver.quit()
