import time
import csv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from textblob import TextBlob

# Configuration de Selenium
url = "https://fr.investing.com/commodities/crude-oil-commentary"
options = Options()
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

# Fonction pour extraire les commentaires
def extract_comments():
    """
    Extraire tous les commentaires de la section #comments_new.
    """
    comments = []
    try:
        # Trouver la section des commentaires
        comments_section = driver.find_element(By.ID, "comments_new")
        print("Section des commentaires trouvée.")
        
        # Attendre que les commentaires soient chargés dans la section
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.break-words.leading-5"))
        )
        
        # Trouver tous les commentaires dans la section
        comment_elements = comments_section.find_elements(By.CSS_SELECTOR, "div.break-words.leading-5")
        print(f"Nombre de commentaires trouvés : {len(comment_elements)}")
        
        # Ajouter chaque commentaire dans une liste
        for element in comment_elements:
            comment_text = element.text.strip()
            if comment_text:  # Ne garder que les textes non vides
                comments.append(comment_text)
    except Exception as e:
        print(f"Erreur lors de l'extraction des commentaires : {e}")
    return comments

# Fonction pour analyser le sentiment d'un commentaire
def analyze_sentiment(comment):
    """
    Analyser le sentiment d'un commentaire.
    """
    analysis = TextBlob(comment)
    polarity = analysis.sentiment.polarity  # Score entre -1 (négatif) et 1 (positif)
    if polarity > 0:
        return "Positif"
    elif polarity < 0:
        return "Négatif"
    else:
        return "Neutre"

# Fonction pour enregistrer les commentaires et leurs sentiments dans un fichier CSV
def save_to_csv(data, filename="comments_sentiment.csv"):
    """
    Enregistrer les commentaires et leurs sentiments dans un fichier CSV.
    """
    # Ouverture du fichier CSV en mode append pour ajouter les nouvelles données
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Si le fichier est vide, écrire les en-têtes
        if file.tell() == 0:
            writer.writerow(["Commentaire", "Sentiment"])
        # Écrire chaque commentaire et son sentiment
        for comment, sentiment in data:
            writer.writerow([comment, sentiment])

try:
    print("Chargement de la page...")
    driver.get(url)

    # Attendre que la page et un élément visible soient chargés
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))  # Attendre un élément visible comme un titre
    )
    
    print("Page chargée, extraction des commentaires...")

    while True:
        # Extraire les commentaires
        comments = extract_comments()

        if not comments:
            print("Aucun commentaire trouvé.")
        else:
            comments_with_sentiment = []
            # Analyser les sentiments des commentaires
            for comment in comments:
                sentiment = analyze_sentiment(comment)
                comments_with_sentiment.append((comment, sentiment))
                # Afficher dans la console
                print(f"Commentaire : {comment} | Sentiment : {sentiment}")

            # Enregistrer les commentaires et leurs sentiments dans un fichier CSV
            save_to_csv(comments_with_sentiment)

        # Attendre un certain temps avant de récupérer à nouveau
        time.sleep(30)

except Exception as e:
    print(f"Erreur : {e}")

finally:
    driver.quit()
