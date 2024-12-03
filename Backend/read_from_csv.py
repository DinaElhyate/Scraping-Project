from flask import Flask, jsonify
import csv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Fonction pour lire les données du fichier CSV
def read_from_csv(filename="comments_sentiment.csv"):
    """
    Lire les commentaires et leurs sentiments depuis un fichier CSV.
    """
    comments_data = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Sauter l'en-tête
            for row in reader:
                comments_data.append({"comment": row[0], "sentiment": row[1]})
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV : {e}")
    return comments_data

@app.route('/comments', methods=['GET'])
def get_comments():
    """
    Endpoint pour obtenir les commentaires et leurs sentiments.
    """
    comments = read_from_csv()  # Lire les données du fichier CSV
    if not comments:
        return jsonify({"message": "Aucun commentaire trouvé."}), 404
    return jsonify(comments)

@app.route('/comments/stats', methods=['GET'])
def get_comments_stats():
    """
    Endpoint pour obtenir le nombre de commentaires par sentiment.
    """
    comments = read_from_csv()  # Lire les données du fichier CSV
    if not comments:
        return jsonify({"message": "Aucun commentaire trouvé."}), 404
    
    sentiment_counts = {}
    for comment in comments:
        sentiment = comment["sentiment"]
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

    return jsonify(sentiment_counts)
if __name__ == "__main__":
    app.run(debug=True, port=5002)

