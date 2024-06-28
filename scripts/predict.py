import pandas as pd
from datetime import datetime, timedelta
import joblib

def predict_weather(file_path, model_path):
    # Charger les données météorologiques
    data = pd.read_csv(file_path)

    # Charger le modèle pré-entraîné
    model = joblib.load(model_path)

    # Gérer les valeurs manquantes en utilisant la méthode de remplissage
    data['temperature_2m'].fillna(method='ffill', inplace=True)

    # Préparer les données pour la prédiction
    data['date'] = pd.to_datetime(data['date'])
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['day'] = data['date'].dt.day
    data['hour'] = data['date'].dt.hour

    # Sélectionner les mêmes caractéristiques que lors de l'entraînement
    features = data[['year', 'month', 'day', 'hour', 'temperature_2m']]

    # Prédire en utilisant le modèle pré-entraîné
    data['predicted_temperature_2m'] = model.predict(features)

    # Sauvegarder les prédictions dans un nouveau fichier CSV
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"./predicted_weather_{timestamp}.csv"
    data[['date', 'predicted_temperature_2m']].to_csv(filename, index=False)
    return filename