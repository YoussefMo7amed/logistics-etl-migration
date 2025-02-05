from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

from config.settings import MONGO_URI

# Load environment variables from the .env file
load_dotenv()


def get_mongo_client():
    """
    Connect to MongoDB using the credentials from the .env file.
    Handles potential connection errors and prints appropriate messages.
    """
    try:
        client = MongoClient(
            MONGO_URI, serverSelectionTimeoutMS=5000
        )  # 5-second timeout
        client.admin.command("ping")  # Ping the server to validate the connection
        print(f"Connected to MongoDB")
        return client

    except ConnectionFailure as e:
        # Handle connection errors
        print(f"Failed to connect to MongoDB: {e}")
        print(
            "Please ensure the MongoDB service is running and the connection details are correct."
        )

    except ValueError as ve:
        # Handle missing environment variables
        print(f"Error: {ve}")

    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
