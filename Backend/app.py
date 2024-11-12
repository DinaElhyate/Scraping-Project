from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from datetime import datetime
import os
url = "https://fr.investing.com/commodities/crude-oil-commentary"
csv_filename = 'data.csv'
# Vérifier si le fichier existe déjà pour ne pas réécrire l'en-tête
file_exists = os.path.exists(csv_filename)
# Configurer le navigateur Chrome
options = Options()
options.binary_location = "/usr/bin/google-chrome"  # chemin typique sur Ubuntu
# options.add_argument('--headless')  # Décommenter si vous voulez exécuter en mode sans tête
try:
    print("Initialisation du pilote...")
    # Initialiser le driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Boucle infinie pour récupérer les données
    while True:
        print("Chargement de la page...")
        # Charger la page
        driver.get(url)
        # Attendre que les éléments soient visibles
        try:
            print("Attente des éléments...")
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="instrument-price-last"]'))
            )
            # Trouver les éléments désirés dans la structure HTML
            price = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-last"]').text.strip()  # Prix actuel
            change = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-change"]').text.strip()  # Changement
            change_percent = driver.find_element(By.CSS_SELECTOR, '[data-test="instrument-price-change-percent"]').text.strip()  # Changement en pourcentage
            time_label = driver.find_element(By.CSS_SELECTOR, '[data-test="trading-time-label"]').text.strip()  # Heure de mise à jour
            
            # Récupérer l'heure actuelle pour l'horodatage
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Ouvrir le fichier en mode ajout pour écrire les résultats
            with open(csv_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                # Écrire l'en-tête dans le fichier CSV uniquement si le fichier est nouveau
                if not file_exists:
                    writer.writerow(["Timestamp", "Prix actuel", "Changement", "Changement (%)", "Heure de mise à jour"])
                    file_exists = True  # Mettre à jour le statut pour éviter de réécrire l'en-tête à l'avenir
                # Écrire les résultats dans le fichier CSV
                writer.writerow([timestamp, price, change, change_percent, time_label])
            # Afficher les résultats
            print(f"Timestamp: {timestamp}")
            print(f"Prix actuel Pétrole brut : {price}")
            print(f"Changement : {change}")
            print(f"Changement en pourcentage : {change_percent}")
            print(f"Heure  : {time_label}")
            print("-" * 40)  # Ligne de séparation pour la lisibilité
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
        # Attendre 10 secondes avant la prochaine requête
        time.sleep(10)
except Exception as e:
    print(f"Erreur lors de l'initialisation du pilote : {e}")
finally:
    # Fermer le navigateur si le driver a été initialisé
    if 'driver' in locals():
        driver.quit()