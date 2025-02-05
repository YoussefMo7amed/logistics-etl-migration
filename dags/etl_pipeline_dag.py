from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from etl.etl_pipeline import first_pipeline, second_pipeline, third_pipeline
from utils.helpers import send_failure_email

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def send_failure_notification(context):
    send_failure_email(context)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.today(),
    "retries": 3,
    "on_failure_callback": send_failure_notification,
}

dag = DAG(
    "mongo_to_mysql_etl_pipeline_dag",
    default_args=default_args,
    description="A simple ETL pipeline DAG",
    schedule="@daily",
)

first_pipeline_task = PythonOperator(
    task_id="first_pipeline",
    python_callable=first_pipeline,
    dag=dag,
)

second_pipeline_task = PythonOperator(
    task_id="second_pipeline",
    python_callable=second_pipeline,
    dag=dag,
)

third_pipeline_task = PythonOperator(
    task_id="third_pipeline",
    python_callable=third_pipeline,
    dag=dag,
)

# Define the order of tasks
first_pipeline_task >> second_pipeline_task >> third_pipeline_task
