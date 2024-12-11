from flask import Flask, jsonify, request
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Nom du fichier CSV
csv_filename = 'prediction.csv'
csv_filename2 = 'prediction_rf.csv'

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
# Route pour lire toutes les données du fichier CSV
@app.route('/api/data/predictionrf', methods=['GET'])
def get_prediction_rf_data():
    # Vérifier si le fichier CSV existe
    if not os.path.exists(csv_filename2):
        return jsonify({"error": "Le fichier CSV n'existe pas."}), 404

    data = []
    try:
        with open(csv_filename2, mode='r') as file:
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


@app.route('/api/data/comparison', methods=['GET'])
def compare_predictions():
    # Charger les données du premier CSV (régression linéaire)
    if not os.path.exists(csv_filename):
        return jsonify({"error": "Le fichier CSV de régression linéaire n'existe pas."}), 404

    linear_data = []
    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            # Limiter à 100 lignes
            for i, row in enumerate(reader):
                if i >= 100:
                    break
                linear_data.append({
                    "Timestamp": row["Timestamp"],
                    "Prix actuel": float(row["Prix actuel"]),
                    "Prédiction du prochain prix": float(row["Prédiction du prochain prix"]),
                })
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la lecture du fichier CSV (régression linéaire): {str(e)}"}), 500

    # Charger les données du second CSV (Random Forest)
    if not os.path.exists(csv_filename2):
        return jsonify({"error": "Le fichier CSV de Random Forest n'existe pas."}), 404

    rf_data = []
    try:
        with open(csv_filename2, mode='r') as file:
            reader = csv.DictReader(file)
            # Limiter à 100 lignes
            for i, row in enumerate(reader):
                if i >= 100:
                    break
                rf_data.append({
                    "Timestamp": row["Timestamp"],
                    "Prix actuel": float(row["Prix actuel"]),
                    "Prédiction du prochain prix": float(row["Prédiction du prochain prix"]),
                })
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la lecture du fichier CSV (Random Forest): {str(e)}"}), 500

    # Comparer les résultats des deux modèles
    if len(linear_data) != len(rf_data):
        return jsonify({"error": "Les fichiers CSV ont un nombre de lignes différent."}), 400

    comparison_result = []
    for linear_item, rf_item in zip(linear_data, rf_data):
        # Calculer l'erreur absolue pour chaque modèle par rapport au prix actuel
        linear_error = abs(linear_item["Prédiction du prochain prix"] - linear_item["Prix actuel"])
        rf_error = abs(rf_item["Prédiction du prochain prix"] - rf_item["Prix actuel"])

        # Déterminer quel modèle a la plus petite erreur
        if linear_error < rf_error:
            most_accurate_model = "Régression Linéaire"
        elif rf_error < linear_error:
            most_accurate_model = "Random Forest"
        else:
            # Si les erreurs sont égales, choisir le modèle dont la prédiction est la plus proche du prix actuel
            linear_diff = abs(linear_item["Prédiction du prochain prix"] - linear_item["Prix actuel"])
            rf_diff = abs(rf_item["Prédiction du prochain prix"] - rf_item["Prix actuel"])

            if linear_diff < rf_diff:
                most_accurate_model = "Régression Linéaire"
            elif rf_diff < linear_diff:
                most_accurate_model = "Random Forest"
            else:
                # Si les deux différences sont égales, dire qu'il y a une égalité
                most_accurate_model = "Égalité"

        comparison_result.append({
            "Timestamp": linear_item["Timestamp"],
            "Prix actuel": linear_item["Prix actuel"],
            "Linear Prediction": linear_item["Prédiction du prochain prix"],
            "Random Forest Prediction": rf_item["Prédiction du prochain prix"],
            "Linear Error": linear_error,
            "Random Forest Error": rf_error,
            "Most Accurate Model": most_accurate_model,
            "Difference": linear_item["Prédiction du prochain prix"] - rf_item["Prédiction du prochain prix"]
        })

    # Retourner la comparaison des prédictions et l'algorithme le plus précis en JSON
    return jsonify(comparison_result), 200


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
