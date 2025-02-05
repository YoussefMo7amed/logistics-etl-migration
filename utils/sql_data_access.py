from sqlalchemy.orm import sessionmaker
from models.sql.sql_models import *
from connections.sql_connector import get_mysql_engine
from typing import List, Dict, Type
from functools import lru_cache

# Constants
BATCH_SIZE = 1000

# Map table names to SQLAlchemy model classes
TABLE_MAPPING = {
    "countries": Country,
    "cities": City,
    "zones": Zone,
    "addresses": Address,
    "receivers": Receiver,
    "stars": Star,
    "orders": Order,
    "cod_payments": CodPayment,
    "confirmations": Confirmation,
    "trackers": Tracker,
}


@lru_cache(maxsize=1)
def get_session():
    """
    Creates and returns a SQLAlchemy session using connection pooling.
    Cached to avoid multiple session creations.
    """
    engine = get_mysql_engine()
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


from sqlalchemy import text


def write_query_to_read(query: str):
    """
    Executes a raw SQL query with optimized session handling and returns the results.

    Args:
        query: SQL query string to execute

    Returns:
        List of results from the executed query.
    """
    session = get_session()
    result = None

    try:
        # Execute the query
        result = session.execute(text(query))
        # Fetch all results and return them
        return result.fetchall()  # Fetch all rows returned by the query
    except Exception as e:
        session.rollback()  # Rollback in case of error
        raise
    finally:
        session.close()  # Close the session
        # Explicitly remove session from cache to prevent memory leaks
        get_session.cache_clear()


def get_ids_by_mongo_ids(
    table_name: str,
    mongo_ids: List[str],
    value_name: str = "mongo_id",
    filters: Dict = None,
) -> Dict[str, int]:
    """
    Given a table name and a list of values,
    return a dictionary mapping those values to the corresponding MySQL id.

    Args:
        table_name: Name of the table to query
        mongo_ids: List of values to look up
        value_name: Name of the column to match against (default: "mongo_id")
        filters: Optional dictionary of filter conditions to apply (default: None)

    Returns:
        Dictionary mapping values to MySQL IDs

    Raises:
        ValueError: If table_name is invalid
    """
    if not mongo_ids:
        return {}
    mongo_ids = [str(id_) for id_ in mongo_ids]
    Model = TABLE_MAPPING.get(table_name)
    if not Model:
        raise ValueError(f"Invalid table name provided: {table_name}")

    session = get_session()
    try:
        # Convert list to tuple for better performance in IN clause
        mongo_ids = tuple(set(mongo_ids))

        if len(mongo_ids) > BATCH_SIZE:
            # Process large sets in batches
            result_dict = {}
            for i in range(0, len(mongo_ids), BATCH_SIZE):
                batch_ids = mongo_ids[i : i + BATCH_SIZE]
                query = session.query(Model).with_entities(
                    getattr(Model, value_name), Model.id
                )
                query = query.filter(getattr(Model, value_name).in_(batch_ids))

                # Apply additional filters if provided
                if filters:
                    for key, value in filters.items():
                        query = query.filter(getattr(Model, key) == value)

                batch_results = query.all()
                result_dict.update({value: id_ for value, id_ in batch_results})
            return result_dict
        else:
            # Process small sets in one query
            query = session.query(Model).with_entities(
                getattr(Model, value_name), Model.id
            )
            query = query.filter(getattr(Model, value_name).in_(mongo_ids))

            # Apply additional filters if provided
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(Model, key) == value)

            results = query.all()
            return {value: id_ for value, id_ in results}
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


from typing import Dict, List, Tuple


def get_address_id_and_type_by_mongo_ids(
    mongo_ids: List[str],
) -> Dict[str, List[Tuple[int, str]]]:
    """
    Given a list of mongo_ids, return a dictionary mapping those values to the corresponding MySQL id and type.

    Args:
        mongo_ids: List of mongo_ids to look up

    Returns:
        Dictionary mapping mongo_ids to lists of tuples (MySQL ID, type)
    """
    if not mongo_ids:
        return {}

    session = get_session()
    try:
        # Convert list to tuple for better performance in IN clause
        mongo_ids = tuple(set(mongo_ids))

        result_dict = {}
        if len(mongo_ids) > BATCH_SIZE:
            # Process large sets in batches
            for i in range(0, len(mongo_ids), BATCH_SIZE):
                batch_ids = mongo_ids[i : i + BATCH_SIZE]
                query = session.query(Address).with_entities(
                    Address.order_mongo_id, Address.id, Address.type
                )
                query = query.filter(Address.order_mongo_id.in_(batch_ids))
                batch_results = query.all()

                for order_mongo_id, id_, type_ in batch_results:
                    if order_mongo_id not in result_dict:
                        result_dict[order_mongo_id] = []
                    result_dict[order_mongo_id].append((id_, type_))
        else:
            # Process small sets in one query
            query = session.query(Address).with_entities(
                Address.order_mongo_id, Address.id, Address.type
            )
            query = query.filter(Address.order_mongo_id.in_(mongo_ids))
            results = query.all()

            for order_mongo_id, id_, type_ in results:
                if order_mongo_id not in result_dict:
                    result_dict[order_mongo_id] = []
                result_dict[order_mongo_id].append((id_, type_))

        return result_dict
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


# Example usage:
# if __name__ == "__main__":
#     # Suppose you have these mongo_ids for countries
#     mongo_ids = ["67a210bf6261b52121ab373b", "67a210bf6261b5221ab3741"]
#     id_mapping = get_ids_by_mongo_ids("cities", mongo_ids)
#     print(id_mapping)
