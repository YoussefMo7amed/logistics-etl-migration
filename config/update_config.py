import json

CONFIG_PATH = "config/config.json"


def update_last_processed_id(collection_name, last_id):
    """Update last processed `_id` for a specific collection in config.json"""
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    config["last_processed_ids"][collection_name] = str(last_id)  # Store `_id`

    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config, config_file, indent=2)
