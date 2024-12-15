from flask import Flask, jsonify, request
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
csv_filename = 'prediction.csv'
csv_filename2 = 'prediction_rf.csv'

# Route pour lire les données du CSV

@app.route('/api/data/prediction', methods=['GET'])
def get_data():
    if not os.path.exists(csv_filename):
        return jsonify({"error": "Le fichier CSV n'existe pas."}), 404

    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            expected_headers = [
                "Timestamp", "Prix actuel", "Changement", "Changement (%)",
                "Heure de mise à jour", 
                "Prédiction (Régression Linéaire)", "Prédiction pour 5 minutes (Régression Linéaire)",
                "Prédiction (Random Forest)", "Prédiction pour 5 minutes (Random Forest)"
            ]

            if headers != expected_headers:
                return jsonify({
                    "error": "Les en-têtes du fichier CSV ne correspondent pas.",
                    "found_headers": headers,
                    "expected_headers": expected_headers
                }), 400

            data = [
                {
                    "Timestamp": row["Timestamp"],
                    "Prix actuel": float(row["Prix actuel"]),
                    "Changement": row["Changement"],
                    "Changement (%)": row["Changement (%)"],
                    "Heure de mise à jour": row["Heure de mise à jour"],
                    "Prédiction (Régression Linéaire)": float(row["Prédiction (Régression Linéaire)"]),
                    "Prédiction pour 5 minutes (Régression Linéaire)": float(row["Prédiction pour 5 minutes (Régression Linéaire)"]),
                    "Prédiction (Random Forest)": float(row["Prédiction (Random Forest)"]),
                    "Prédiction pour 5 minutes (Random Forest)": float(row["Prédiction pour 5 minutes (Random Forest)"])
                }
                for row in reader
            ]
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la lecture du fichier CSV: {str(e)}"}), 500

    return jsonify(data), 200

# Route pour lire toutes les données du fichier CSV
@app.route('/api/data/predictionrf', methods=['GET'])
def get_prediction_rf_data():
    if not os.path.exists(csv_filename2):
        return jsonify({"error": "Le fichier CSV n'existe pas."}), 404

    data = []
    try:
        with open(csv_filename2, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
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

    return jsonify(data), 200

@app.route('/api/data/compare', methods=['GET'])
def compare_algorithms_with_next_price():
    if not os.path.exists(csv_filename):
        return jsonify({"error": "Le fichier CSV n'existe pas."}), 404

    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            data = [
                {
                    "Timestamp": row["Timestamp"],
                    "Prix actuel": float(row["Prix actuel"]),
                    "Prédiction (Régression Linéaire)": float(row["Prédiction (Régression Linéaire)"]),
                    "Prédiction (Random Forest)": float(row["Prédiction (Random Forest)"])
                }
                for row in reader
            ]
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la lecture du fichier CSV: {str(e)}"}), 500

    results = []
    total_linear_error = 0
    total_rf_error = 0
    total_actual_price = 0

    for i in range(len(data) - 1):  
        current_row = data[i]
        next_row = data[i + 1]  

        actual_next_price = next_row["Prix actuel"]  
        linear_regression_error = abs(actual_next_price - current_row["Prédiction (Régression Linéaire)"])
        random_forest_error = abs(actual_next_price - current_row["Prédiction (Random Forest)"])

        linear_regression_error_percentage = (linear_regression_error / actual_next_price) * 100
        random_forest_error_percentage = (random_forest_error / actual_next_price) * 100

        total_linear_error += linear_regression_error_percentage
        total_rf_error += random_forest_error_percentage
        total_actual_price += actual_next_price

        if linear_regression_error < random_forest_error:
            best_algorithm = "Régression Linéaire"
        elif linear_regression_error > random_forest_error:
            best_algorithm = "Random Forest"
        else:
            best_algorithm = "Égalité"

        results.append({
            "Timestamp": current_row["Timestamp"],
            "Prix actuel": current_row["Prix actuel"],
            "Prix actuel suivant": actual_next_price,
            "Prédiction (Régression Linéaire)": current_row["Prédiction (Régression Linéaire)"],
            "Prédiction (Random Forest)": current_row["Prédiction (Random Forest)"],
            "Meilleur algorithme": best_algorithm,
            "Erreur Régression Linéaire (%)": linear_regression_error_percentage,
            "Erreur Random Forest (%)": random_forest_error_percentage
        })

    if total_linear_error < total_rf_error:
        overall_best_algorithm = "Régression Linéaire"
    elif total_linear_error > total_rf_error:
        overall_best_algorithm = "Random Forest"
    else:
        overall_best_algorithm = "Égalité"

    return jsonify({
        "détails": results,
        "Meilleur algorithme global": overall_best_algorithm,
        "Erreur totale Régression Linéaire (%)": total_linear_error,
        "Erreur totale Random Forest (%)": total_rf_error
    }), 200




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
                if row["Timestamp"].startswith(timestamp):  
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
