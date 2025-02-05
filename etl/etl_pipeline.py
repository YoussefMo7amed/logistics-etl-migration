from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List
from functools import partial
from etl.extract import extract_data
from etl.transform import *
from etl.load import *

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_collection(
    collection_name: str, transform_func: Callable, load_func: Callable, data=None
) -> None:
    """Process a single collection with transformation and loading."""
    try:
        print(f"Starting processing of collection: {collection_name}")
        data_batches = extract_data(collection_name) if data is None else data
        print(f"Successfully extracted data for collection: {collection_name}")

        for batch in data_batches:
            print(f"Transforming batch for collection: {collection_name}")
            df = transform_func(batch)
            print(f"Successfully transformed batch for collection: {collection_name}")

            print(f"Loading transformed data for collection: {collection_name}")
            load_func(df)
            print(f"Successfully loaded data for collection: {collection_name}")

        print(f"Completed processing collection: {collection_name}")
    except Exception as e:
        print(f"Error processing {collection_name}: {str(e)}")


def first_pipeline(max_workers: int = 3) -> None:
    """
    Execute the ETL pipeline with parallel processing.

    Args:
        max_workers: Maximum number of concurrent threads.
    """
    collection_configs = {
        "star": (transform_star_data, load_star_data),
        "country": (transform_country_data, load_country_data),
        "city": (transform_city_data, load_city_data),
        "zone": (transform_zone_data, load_zone_data),
        "receiver": (transform_receiver_data, load_receiver_data),
    }

    process_collection(
        "star", *collection_configs["star"]
    )  # Ensure star is loaded first

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(
            lambda cfg: process_collection(*cfg),
            [
                (name, *funcs)
                for name, funcs in collection_configs.items()
                if name != "star"
            ],
        )


def second_pipeline(max_workers: int = 3) -> None:
    """
    Execute the second ETL pipeline for address data.
    """
    order_data = list(extract_data("order"))  # Convert to list to avoid exhaustion
    process_collection(
        "order", transform_pickup_address_data, load_address_data, order_data
    )
    process_collection(
        "order", transform_dropoff_address_data, load_address_data, order_data
    )


def third_pipeline() -> None:
    """
    Execute the third ETL pipeline for order and related data.
    """
    order_data = list(extract_data("order"))
    process_collection("order", transform_order_data, load_order_data, order_data)

    # # TODO: take the order sql ids, and pass it with transform function instead of re-access the DB again (since they are the same order and we need the id)
    process_collection(
        "order", transform_confirmation_data, load_confirmation_data, order_data
    )
    process_collection(
        "order", transform_cod_payment_data, load_codpayment_data, order_data
    )
    process_collection("tracker", transform_tracker_data, load_tracker_data)


def run_pipeline():
    """
    Main function to execute ETL pipelines sequentially.
    """
    try:
        print("Starting first ETL pipeline...")
        first_pipeline()
        print("First pipeline completed successfully")

        print("Starting second ETL pipeline...")
        second_pipeline()
        print("Second pipeline completed successfully")

        print("Starting third ETL pipeline...")
        third_pipeline()
        print("Third pipeline completed successfully")

    except Exception as e:
        print(f"Error executing pipelines: {str(e)}")
