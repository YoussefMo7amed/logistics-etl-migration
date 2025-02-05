from connections.mongo_connector import get_mongo_client
from config.settings import (
    LAST_PROCESSED_IDS,
    ETL_BATCH_SIZE,
    LAST_UPDATED,
    MONGO_DATABASE,
)
from config.update_config import update_last_processed_id

client = get_mongo_client()
db = client[MONGO_DATABASE]

COLLECTIONS = {
    "country": db["country"],
    "zone": db["zone"],
    "star": db["star"],
    "city": db["city"],
    "receiver": db["receiver"],
    "tracker": db["tracker"],
    "order": db["order"],
}


def extract_data(collection_name):
    """Extract data from a MongoDB collection using `_id` pagination."""
    if collection_name not in COLLECTIONS:
        raise KeyError(
            f"Collection '{collection_name}' not found. Available collections: {list(COLLECTIONS.keys())}"
        )

    collection = COLLECTIONS[collection_name]
    last_id = LAST_PROCESSED_IDS.get(collection_name)

    while True:
        query = {"updatedAt": {"$gt": LAST_UPDATED}}
        if last_id:
            query["_id"] = {"$gt": last_id}

        cursor = collection.find(query).sort("_id").limit(ETL_BATCH_SIZE)
        batch = list(cursor)

        if not batch:
            print(f"No more records for {collection_name}")
            break

        yield batch
        if batch:
            last_id = batch[-1]["_id"]
            # update_last_processed_id(collection_name, last_id)
