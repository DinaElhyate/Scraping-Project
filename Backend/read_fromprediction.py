from flask import Flask, jsonify, request
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Nom du fichier CSV
csv_filename = 'prediction.csv'

# Route pour lire les données du CSV
@app.route('/api/data/prediction', methods=['GET'])
def get_data():
    # Vérifier si le fichier CSV existe
    if not os.path.exists(csv_filename):
        return jsonify({"error": "Le fichier CSV n'existe pas."}), 404

    data = []
    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convertir les données en dictionnaire
                data.append({
                    "Timestamp": row["Timestamp"],
                    "Prix actuel": float(row["Prix actuel"]),
                    "Changement": row["Changement"],
                    "Changement (%)": row["Changement (%)"],
                    "Heure de mise à jour": row["Heure de mise à jour"],
                    "Prédiction du prochain prix": float(row["Prédiction du prochain prix"]),
                    "Prédiction pour 5 minutes": float(row["Prédiction pour 5 minutes"])
                })
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la lecture du fichier CSV: {str(e)}"}), 500

    # Retourner les données en JSON
    return jsonify(data), 200

# Route pour lire les données filtrées par Timestamp
@app.route('/api/data/<timestamp>', methods=['GET'])
def get_data_by_timestamp(timestamp):
    if not os.path.exists(csv_filename):
        return jsonify({"error": "Le fichier CSV n'existe pas."}), 404

    data = []
    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Timestamp"].startswith(timestamp):  # Filtrer par timestamp partiel
                    data.append({
                        "Timestamp": row["Timestamp"],
                        "Prix actuel": float(row["Prix actuel"]),
                        "Changement": row["Changement"],
                        "Changement (%)": row["Changement (%)"],
                        "Heure de mise à jour": row["Heure de mise à jour"],
                        "Prédiction du prochain prix": float(row["Prédiction du prochain prix"]),
                        "Prédiction pour 5 minutes": float(row["Prédiction pour 5 minutes"])
                    })
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la lecture du fichier CSV: {str(e)}"}), 500

    if not data:
        return jsonify({"message": f"Aucune donnée trouvée pour le timestamp {timestamp}."}), 404

    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True, port=5003)
