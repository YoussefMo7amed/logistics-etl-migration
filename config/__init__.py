from .settings import (
    MONGO_URI,
    SQL_CONFIG,
    ETL_BATCH_SIZE,
    LAST_UPDATED,
    update_last_updated,
)


# You can also define a function to get the config values if needed
def get_config():
    return {
        "MONGO_URI": MONGO_URI,
        "SQL_CONFIG": SQL_CONFIG,
        "ETL_BATCH_SIZE": ETL_BATCH_SIZE,
        "LAST_UPDATED": LAST_UPDATED,
    }
