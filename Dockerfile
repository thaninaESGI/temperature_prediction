# Utiliser l'image de base Apache Airflow avec la dernière version
FROM apache/airflow:2.9.2

# Installer gosu
USER root
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends gosu; \
    rm -rf /var/lib/apt/lists/*

# Copier les fichiers nécessaires dans le conteneur avec le bon propriétaire
COPY --chown=airflow:root . /app
WORKDIR /app

# Copier le script d'initialisation
COPY init_script.sh /app/init_script.sh
RUN chmod +x /app/init_script.sh

# Passer à l'utilisateur airflow
USER airflow

# Installer les dépendances
RUN pip install -r requirements.txt

# Exposer le port sur lequel l'application Flask va tourner (si nécessaire)
EXPOSE 5000

# Utiliser gosu pour démarrer l'application avec l'utilisateur airflow
CMD ["gosu", "airflow", "python", "api.py"]
