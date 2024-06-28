import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

def train_model(data_path, model_path):
    # Lire les données à partir du fichier CSV
    data = pd.read_csv(data_path)

    # Convertir la colonne 'date' en type datetime
    data['date'] = pd.to_datetime(data['date'])

    # Gérer les valeurs manquantes en utilisant la méthode de remplissage
    data['temperature_2m'].fillna(method='ffill', inplace=True)

    # Créer des caractéristiques temporelles à partir de la colonne 'date'
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['day'] = data['date'].dt.day
    data['hour'] = data['date'].dt.hour

    # Décaler la température de 24 heures pour créer la variable cible
    data['temperature_next_day'] = data['temperature_2m'].shift(-24)

    # Supprimer les dernières 24 lignes car elles n'ont pas de valeur de température pour le jour suivant
    data.dropna(subset=['temperature_next_day'], inplace=True)

    # Définir les caractéristiques (X) et la variable cible (y)
    X = data[['year', 'month', 'day', 'hour', 'temperature_2m']]
    y = data['temperature_next_day']

    # Diviser les données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Créer et entraîner le modèle de régression linéaire
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Faire des prédictions sur l'ensemble de test
    y_pred = model.predict(X_test)

    # Évaluer le modèle
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Mean Squared Error: {mse}")
    print(f"R-squared: {r2}")

    # Enregistrer le modèle dans un fichier
    joblib.dump(model, model_path)
    print(f"Model has been saved to {model_path}")

    return model_path