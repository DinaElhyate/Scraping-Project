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

url = "https://fr.investing.com/commodities/crude-oil-commentary"
options = Options()
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

def extract_comments():
    """
    Extraire tous les commentaires de la section #comments_new.
    """
    comments = []
    try:
        comments_section = driver.find_element(By.ID, "comments_new")
        print("Section des commentaires trouvée.")
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.break-words.leading-5"))
        )
        
        comment_elements = comments_section.find_elements(By.CSS_SELECTOR, "div.break-words.leading-5")
        print(f"Nombre de commentaires trouvés : {len(comment_elements)}")
        
        for element in comment_elements:
            comment_text = element.text.strip()
            if comment_text:  
                comments.append(comment_text)
    except Exception as e:
        print(f"Erreur lors de l'extraction des commentaires : {e}")
    return comments

def analyze_sentiment(comment):
    """
    Analyser le sentiment d'un commentaire.
    """
    analysis = TextBlob(comment)
    polarity = analysis.sentiment.polarity  
    if polarity > 0:
        return "Positif"
    elif polarity < 0:
        return "Négatif"
    else:
        return "Neutre"

def save_to_csv(data, filename="comments_sentiment.csv"):
    """
    Enregistrer les commentaires et leurs sentiments dans un fichier CSV.
    """
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["Commentaire", "Sentiment"])
        for comment, sentiment in data:
            writer.writerow([comment, sentiment])

try:
    print("Chargement de la page...")
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')) 
    )
    
    print("Page chargée, extraction des commentaires...")

    while True:
        comments = extract_comments()

        if not comments:
            print("Aucun commentaire trouvé.")
        else:
            comments_with_sentiment = []
            for comment in comments:
                sentiment = analyze_sentiment(comment)
                comments_with_sentiment.append((comment, sentiment))
                print(f"Commentaire : {comment} | Sentiment : {sentiment}")

            save_to_csv(comments_with_sentiment)

        time.sleep(30)

except Exception as e:
    print(f"Erreur : {e}")

finally:
    driver.quit()
