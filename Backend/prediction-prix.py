from datetime import datetime
import numpy as np
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import locale

url = "https://fr.investing.com/commodities/crude-oil-commentary"
csv_filename = 'prediction.csv'

options = Options()
options.binary_location = "/usr/bin/firefox"
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

lr_model = LinearRegression()
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

price_data = []  
data_batch = []

def write_csv_header():
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp", "Prix actuel", "Changement", "Changement (%)", "Heure de mise à jour",
                "Prédiction (Régression Linéaire)", "Prédiction pour 5 minutes (Régression Linéaire)",
                "Prédiction (Random Forest)", "Prédiction pour 5 minutes (Random Forest)"
            ])

write_csv_header()

try:
    print("Chargement de la page...")
    driver.get(url) 

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="instrument-price-last"]'))
            )

            locale.setlocale(locale.LC_NUMERIC, 'fr_FR.UTF-8')

            # Code pour récupérer et formater le prix
            price = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-last"]').text.strip()
            price = float(price.replace(',', '.'))  # Remplacer la virgule par un point pour convertir en float
            change = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-change"]').text.strip()
            change_percent = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-change-percent"]').text.strip()
            time_label = driver.find_element(By.CSS_SELECTOR, '[data-test="trading-time-label"]').text.strip()
            timestamp = datetime.now()

            price_data.append((timestamp, price))
            if len(price_data) > 10: 
                price_data.pop(0)

            if len(price_data) >= 2: 
                base_time = price_data[0][0]
                X = np.array([(t[0] - base_time).total_seconds() for t in price_data]).reshape(-1, 1)
                y = np.array([t[1] for t in price_data])
                
                lr_model.fit(X, y)
                rf_model.fit(X, y)

                next_time = (price_data[-1][0] - base_time).total_seconds() + 10
                predicted_lr_next = lr_model.predict(np.array([[next_time]]))[0]
                predicted_rf_next = rf_model.predict(np.array([[next_time]]))[0]

                future_time = (price_data[-1][0] - base_time).total_seconds() + 300
                predicted_lr_5min = lr_model.predict(np.array([[future_time]]))[0]
                predicted_rf_5min = rf_model.predict(np.array([[future_time]]))[0]
            else:
                predicted_lr_next = predicted_rf_next = price
                predicted_lr_5min = predicted_rf_5min = price

            data_batch.append([
                timestamp.strftime("%Y-%m-%d %H:%M:%S"), price, change, change_percent, time_label,
                predicted_lr_next, predicted_lr_5min, predicted_rf_next, predicted_rf_5min
            ])
            
            if len(data_batch) >= 5:
                with open(csv_filename, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(data_batch)
                data_batch.clear() 

            print(f"Timestamp: {timestamp}, Prix actuel: {price}, Changement: {change}, Pourcentage: {change_percent}, Heure: {time_label}")
            print(f"[LR] Prédiction 10 sec: {predicted_lr_next}, Prédiction 5 min: {predicted_lr_5min}")
            print(f"[RF] Prédiction 10 sec: {predicted_rf_next}, Prédiction 5 min: {predicted_rf_5min}")

        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
        
        time.sleep(10)

except Exception as e:
    print(f"Erreur lors de l'initialisation du pilote : {e}")

finally:
    if 'driver' in locals():
        driver.quit()
