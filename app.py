import streamlit as st
import pandas as pd
import joblib
import datetime
import json
import os

# Charger la configuration depuis le fichier config.json
def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

# Charger le modèle
def load_model(model_path):
    return joblib.load(model_path)

# Préparer les données de prédiction
def prepare_data(date, temperature):
    df = pd.DataFrame({
        'date': [date],
        'temperature_2m': [temperature]
    })
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df = df.drop(columns=['date'])
    df = df[['year', 'month', 'day', 'hour', 'temperature_2m']]  # Assurez-vous de l'ordre des colonnes
    return df

# Faire la prédiction
def predict_weather(date, temperature, model):
    # Préparer les données de prédiction
    data = prepare_data(pd.to_datetime(date), temperature)

    # Prédire en utilisant le modèle pré-entraîné
    prediction = model.predict(data)
    return prediction
# Faire la prédiction
def predict_temperature(model, data):
    prediction = model.predict(data)
    return prediction

# Chemin vers le fichier de configuration
config_file = 'config.json'
config = load_config(config_file)

model_path = config['model_path']
model = load_model(model_path)

st.title('Weather Prediction App')

# Entrée utilisateur pour la date
date_input = st.date_input('Select a date', datetime.date.today())

# Entrée utilisateur pour la température
temperature_input = st.number_input('Enter the temperature (2m)', value=20.0)

# Préparer les données de prédiction
data = prepare_data(pd.to_datetime(date_input), temperature_input)

if st.button('Predict Temperature'):
    prediction = predict_temperature(model, data)
    st.write(f'Temperature prediction for {date_input}: {prediction[0]:.2f}°C')
