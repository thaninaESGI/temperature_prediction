from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os
import json

sys.path.append('/opt/airflow/scripts')

from fetch_weather_data import fetch_weather_data
from predict import predict_weather
from train_model import train_model

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_data_pipeline',
    default_args=default_args,
    description='A simple weather data pipeline',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 6, 28),
    catchup=False,
)

# Charger la configuration depuis le fichier config.json
config = load_config('/opt/airflow/dags/config.json')
df_path=config['df_path']
save_path = config['save_path']
model_path = config['model_path']

fetch_data_task = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    op_kwargs={
        'df_path': df_path,
        'save_path': save_path
    },
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    op_kwargs={
        'data_path': df_path,
        'model_path': model_path
    },
    dag=dag,
)

predict_task = PythonOperator(
    task_id='predict_weather',
    python_callable=predict_weather,
    op_kwargs={
        'file_path': "{{ task_instance.xcom_pull(task_ids='fetch_weather_data')}}",
        'model_path': model_path,
    },
    dag=dag,
)

fetch_data_task >> train_task >> predict_task
