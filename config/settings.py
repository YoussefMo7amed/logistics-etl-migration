# Load environment variables from .env file
from dotenv import load_dotenv
import os
import json
from datetime import datetime


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
SQL_CONFIG = {
    "host": os.getenv("SQL_HOST", "localhost"),
    "user": os.getenv("SQL_USER"),
    "password": os.getenv("SQL_PASSWORD"),
    "database": os.getenv("SQL_DATABASE"),
    "port": int(os.getenv("SQL_PORT", 3306)),
}

# Load ETL configurations from config.json
with open("config/config.json") as config_file:
    etl_config = json.load(config_file)


# ETL Configuration
ETL_BATCH_SIZE = etl_config.get("ETL_BATCH_SIZE", 1000)
LAST_UPDATED = datetime.fromisoformat(
    etl_config.get("last_updated", "2023-10-01T12:00:00Z")
)


def update_last_updated():
    # Load the current configuration
    with open("config/config.json", "r") as config_file:
        config = json.load(config_file)

    # Update the LAST_UPDATED field with the current timestamp
    config["last_updated"] = datetime.now().astimezone().isoformat()

    # Write the updated configuration back to the file
    with open("config/config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)


LAST_PROCESSED_IDS = etl_config["last_processed_ids"]

AIRFLOW_CONFIG = {
    "username": os.getenv("AIRFLOW_USERNAME"),
    "password": os.getenv("AIRFLOW_PASSWORD"),
    "firstname": os.getenv("AIRFLOW_FIRSTNAME"),
    "lastname": os.getenv("AIRFLOW_LASTNAME"),
    "email": os.getenv("AIRFLOW_EMAIL"),
    "role": os.getenv("AIRFLOW_ROLE"),
}
