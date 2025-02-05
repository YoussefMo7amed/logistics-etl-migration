import pandas as pd
from utils.sql_data_access import (
    get_ids_by_mongo_ids,
    get_address_id_and_type_by_mongo_ids,
    write_query_to_read,
)


def convert_id_columns_to_string(df):
    """
    Converts all columns containing '_id' (case insensitive) to string type

    Args:
        df: pandas DataFrame to process

    Returns:
        DataFrame with ID columns converted to string type
    """
    return df.astype({col: str for col in df.columns if "_id" in col.lower()})


def transform_common_datatypes(df):

    if "mongo_id" in df.columns:
        df["mongo_id"] = df["mongo_id"].astype(str)
    if "createdAt" in df.columns:
        df["created_at"] = pd.to_datetime(df["createdAt"]).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    if "updatedAt" in df.columns:
        df["updated_at"] = pd.to_datetime(df["updatedAt"]).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    df.rename(
        columns={
            "firstName": "first_name",
            "lastName": "last_name",
            "orderId": "order_id",
            "firstLine": "first_line",
            "secondLine": "second_line",
            "zoneId": "zone_id",
            "cityId": "city_id",
            "countryId": "country_id",
        },
        inplace=True,
    )
    return df


def transform_zone_data(zoneCollection):
    df = pd.json_normalize(zoneCollection)
    df.rename(
        columns={
            "_id": "mongo_id",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )
    df = convert_id_columns_to_string(df)
    return transform_common_datatypes(df)


def transform_city_data(cityCollection):
    df = pd.json_normalize(cityCollection)
    df.rename(
        columns={
            "_id": "mongo_id",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )
    df = convert_id_columns_to_string(df)
    return transform_common_datatypes(df)


def transform_country_data(countryCollection):
    df = pd.json_normalize(countryCollection)
    df.rename(
        columns={
            "_id": "mongo_id",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )
    df = convert_id_columns_to_string(df)

    return transform_common_datatypes(df)


def transform_address_data(orderCollection, address_type):
    """Extracts and transforms addresses from orders."""

    # Determine the prefix based on the address type
    prefix = f"{address_type}Address."

    # Define the columns to extract
    meta_columns = [
        ["_id"],
        [prefix + "floor"],
        [prefix + "apartment"],
        [prefix + "firstLine"],
        [prefix + "secondLine"],
        [prefix + "district"],
        [prefix + "geoLocation"],
        [prefix + "zone"],
        [prefix + "city"],
        [prefix + "country"],
        "createdAt",
        "updatedAt",
    ]

    # Normalize the JSON data
    df = pd.json_normalize(
        orderCollection,
        record_path=None,
        meta=meta_columns,
    )

    # Rename columns
    df.rename(
        columns={
            "_id": "order_mongo_id",
            prefix + "floor": "floor",
            prefix + "apartment": "apartment",
            prefix + "firstLine": "first_line",
            prefix + "secondLine": "second_line",
            prefix + "district": "district",
            prefix + "geoLocation": "geo_location",
            prefix + "zone": "zone_mongo_id",
            prefix + "city": "city_mongo_id",
            prefix + "country": "country_mongo_id",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )
    df = convert_id_columns_to_string(df)
    # Convert IDs to strings if they exist

    if "zone_mongo_id" in df.columns:
        zone_id_mapping = get_ids_by_mongo_ids("zones", list(df["zone_mongo_id"]))
        df["zone_id"] = df["zone_mongo_id"].map(zone_id_mapping)

    if "city_mongo_id" in df.columns:
        city_id_mapping = get_ids_by_mongo_ids("cities", list(df["city_mongo_id"]))
        df["city_id"] = df["city_mongo_id"].map(city_id_mapping)

    if "country_mongo_id" in df.columns:
        country_id_mapping = get_ids_by_mongo_ids(
            "countries", list(df["country_mongo_id"])
        )
        df["country_id"] = df["country_mongo_id"].map(country_id_mapping)

    if "geo_location" in df.columns:
        df["geo_location"] = df["geo_location"].apply(
            lambda x: f"POINT({x[0]} {x[1]})" if isinstance(x, list) else None
        )
    df["type"] = "pickup" if "pickup" == address_type else "dropoff"
    # Select the relevant columns
    selected_columns = [
        "order_mongo_id",
        "first_line",
        "second_line",
        "district",
        "floor",
        "apartment",
        "geo_location",
        "type",
        "zone_id",
        "city_id",
        "country_id",
        "created_at",
        "updated_at",
    ]

    # Filter out columns that do not exist in the DataFrame
    selected_columns = [col for col in selected_columns if col in df.columns]

    return transform_common_datatypes(df)[selected_columns]


def transform_pickup_address_data(orderCollection):
    """Extracts and transforms pickup addresses from orders."""
    return transform_address_data(orderCollection, "pickup")


def transform_dropoff_address_data(orderCollection):
    """Extracts and transforms drop-off addresses from orders."""
    return transform_address_data(orderCollection, "dropOff")


def transform_receiver_data(receiverCollection):
    df = pd.json_normalize(receiverCollection)
    df.rename(
        columns={
            "_id": "mongo_id",
            "firstName": "first_name",
            "lastName": "last_name",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )
    df = convert_id_columns_to_string(df)
    return transform_common_datatypes(df)


def transform_star_data(starCollection):
    df = pd.json_normalize(starCollection)
    df.rename(
        columns={
            "_id": "mongo_id",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )
    df = convert_id_columns_to_string(df)

    return transform_common_datatypes(df)


def transform_tracker_data(trackerCollection):
    df = pd.json_normalize(trackerCollection)
    df.rename(
        columns={
            "_id": "mongo_id",
            "orderId": "order_number",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        },
        inplace=True,
    )
    df = convert_id_columns_to_string(df)
    query = f"""
    select order_number, id from orders where order_number in 
    ({','.join(map(str, df['order_number'].tolist()))})"""
    order_id_mapping = write_query_to_read(query)
    order_id_mapping = {order[0]: order[1] for order in order_id_mapping}

    df["order_id"] = df["order_number"].map(order_id_mapping)
    return transform_common_datatypes(df)


def transform_cod_payment_data(orderCollection):
    """Transforms COD payment data from MongoDB order documents to a structured format."""
    cod_data = []
    for order in orderCollection:
        cod = order.get("cod", {})
        cod_data.append(
            {
                "mongo_id": order["_id"],
                "amount": cod.get("amount"),
                "collected_amount": cod.get("collectedAmount"),
                "is_paid_back": cod.get("isPaidBack", False),
                "collected_from_business_at": order.get("collectedFromBusiness", {}),
                "created_at": order.get("updatedAt", {}),
                "updated_at": order.get("updatedAt", {}),
            }
        )
    df = pd.DataFrame(cod_data)
    df = convert_id_columns_to_string(df)
    order_id_mapping = get_ids_by_mongo_ids("orders", list(df["mongo_id"]))
    df["order_id"] = df["mongo_id"].map(order_id_mapping)

    return transform_common_datatypes(df)


def transform_confirmation_data(orderCollection):
    """Transforms confirmation data from MongoDB order documents to a structured format."""
    confirmation_data = []
    for order in orderCollection:
        confirmation = order.get("confirmation", {})
        confirmation_data.append(
            {
                "order_mongo_id": order["_id"],
                "is_confirmed": confirmation.get("isConfirmed", False),
                "number_of_sms_trials": confirmation.get("numberOfSmsTrials", 0),
                "created_at": order.get("createdAt"),
                "updated_at": order.get("updatedAt"),
            }
        )

    df = pd.DataFrame(confirmation_data)
    df = convert_id_columns_to_string(df)
    order_id_mapping = get_ids_by_mongo_ids("orders", list(df["order_mongo_id"]))
    df["order_id"] = df["order_mongo_id"].map(order_id_mapping)
    return transform_common_datatypes(df)


def transform_order_data(orderCollection):
    df = pd.json_normalize(orderCollection)

    # Extract relevant fields and rename them to match SQL model
    df = df.rename(
        columns={
            "_id": "mongo_id",
            "orderId": "order_number",
            "type": "type",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
            "receiver": "receiver_mongo_id",
            "star": "star_mongo_id",
        }
    )
    df = convert_id_columns_to_string(df)
    address_id_mapping = get_address_id_and_type_by_mongo_ids(list(df["mongo_id"]))
    # Initialize the pickup and dropoff mappings
    pickup_address_id_mapping = {}
    dropoff_address_id_mapping = {}

    # Populate the mappings based on the type
    for address_id, address_data in address_id_mapping.items():
        for id_num, address_type in address_data:
            if address_type == "pickup":
                pickup_address_id_mapping[address_id] = id_num
            elif address_type == "dropoff":
                dropoff_address_id_mapping[address_id] = id_num
            else:
                print("Unknown address type:", address_type)

    receiver_id_mapping = get_ids_by_mongo_ids(
        "receivers", list(df["receiver_mongo_id"])
    )

    star_id_mapping = get_ids_by_mongo_ids("stars", list(df["star_mongo_id"]))

    df["dropoff_address_id"] = df["mongo_id"].map(dropoff_address_id_mapping)
    df["pickup_address_id"] = df["mongo_id"].map(pickup_address_id_mapping)

    df["receiver_id"] = df["receiver_mongo_id"].map(receiver_id_mapping)
    df["star_id"] = df["star_mongo_id"].map(star_id_mapping)

    # Select relevant columns for the SQL model
    df = df[
        [
            "mongo_id",
            "order_number",
            "type",
            "pickup_address_id",
            "dropoff_address_id",
            "receiver_id",
            "star_id",
            "created_at",
            "updated_at",
        ]
    ]

    return transform_common_datatypes(df)
