from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import insert
from models.sql.sql_models import *
import pandas as pd
from typing import Dict, Any, Type
from contextlib import contextmanager
import logging
from functools import wraps
import time
from connections.sql_connector import get_mysql_engine

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
BATCH_SIZE = 1000


class LoaderError(Exception):
    """Custom exception for loader operations"""

    pass


def timing_decorator(func):
    """Decorator to measure execution time of functions"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(
            f"{func.__name__} took {end_time - start_time:.2f} seconds to execute"
        )
        return result

    return wrapper


class DataLoader:
    def __init__(self):
        self.engine = get_mysql_engine()
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def _prepare_batch(self, df: pd.DataFrame, batch_size: int = BATCH_SIZE):
        """Generator function to yield data in batches"""
        for start in range(0, len(df), batch_size):
            yield df[start : start + batch_size].to_dict("records")

    def _create_upsert_statement(self, model: Type, data: Dict[str, Any]):
        """Create an upsert statement for the given model and data"""
        # Filter out columns that don't exist in the model
        valid_columns = set(model.__table__.columns.keys())
        filtered_data = [
            {k: v for k, v in record.items() if k in valid_columns} for record in data
        ]

        stmt = insert(model).values(filtered_data)

        # Get all columns except id for update
        update_cols = {
            col.name: getattr(stmt.inserted, col.name)
            for col in model.__table__.columns
            if col.name != "id" and col.name in filtered_data[0]
        }

        return stmt.on_duplicate_key_update(**update_cols)

    @timing_decorator
    def bulk_upsert(self, df: pd.DataFrame, model: Type) -> None:
        """
        Perform bulk upsert operation with batching and error handling.

        Args:
            df: DataFrame containing the data to upsert
            model: SQLAlchemy model class
        """
        total_records = len(df)
        processed_records = 0

        try:
            with self.engine.connect() as conn:
                for batch in self._prepare_batch(df):
                    stmt = self._create_upsert_statement(model, batch)
                    conn.execute(stmt)

                    processed_records += len(batch)
                    logger.info(
                        f"Processed {processed_records}/{total_records} records"
                    )

                conn.commit()

            logger.info(
                f"Successfully upserted {total_records} records to {model.__tablename__}"
            )

        except Exception as e:
            logger.error(f"Error during bulk upsert to {model.__tablename__}: {str(e)}")
            raise LoaderError(f"Bulk upsert failed: {str(e)}")


class ModelLoader:
    """Base class for specific model loaders"""

    def __init__(self, model: Type, loader: DataLoader):
        self.model = model
        self.loader = loader

    @timing_decorator
    def load(self, df: pd.DataFrame) -> None:
        """Load data for specific model"""
        self.loader.bulk_upsert(df, self.model)


class CountryLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Country, loader)


class CityLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(City, loader)


class ZoneLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Zone, loader)


class AddressLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Address, loader)


class ReceiverLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Receiver, loader)


class StarLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Star, loader)


class OrderLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Order, loader)


class CodPaymentLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(CodPayment, loader)


class ConfirmationLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Confirmation, loader)


class TrackerLoader(ModelLoader):
    def __init__(self, loader: DataLoader):
        super().__init__(Tracker, loader)


def get_loader(model_type: str) -> ModelLoader:
    """Factory function to create appropriate loader instance"""
    loader = DataLoader()
    loaders = {
        "country": CountryLoader(loader),
        "city": CityLoader(loader),
        "zone": ZoneLoader(loader),
        "address": AddressLoader(loader),
        "receiver": ReceiverLoader(loader),
        "star": StarLoader(loader),
        "order": OrderLoader(loader),
        "codpayment": CodPaymentLoader(loader),
        "confirmation": ConfirmationLoader(loader),
        "tracker": TrackerLoader(loader),
    }
    return loaders.get(model_type.lower())


# Main loading functions
def load_country_data(df: pd.DataFrame) -> None:
    """Load country data"""
    loader = get_loader("country")
    loader.load(df)


def load_city_data(df: pd.DataFrame) -> None:
    """Load city data"""
    loader = get_loader("city")
    loader.load(df)


def load_zone_data(df: pd.DataFrame) -> None:
    """Load zone data"""
    loader = get_loader("zone")
    loader.load(df)


def load_address_data(df: pd.DataFrame) -> None:
    """Load address data"""
    loader = get_loader("address")
    loader.load(df)


def load_receiver_data(df: pd.DataFrame) -> None:
    """Load receiver data"""
    loader = get_loader("receiver")
    loader.load(df)


def load_star_data(df: pd.DataFrame) -> None:
    """Load star data"""
    loader = get_loader("star")
    loader.load(df)


def load_order_data(df: pd.DataFrame) -> None:
    """Load order data"""
    loader = get_loader("order")
    loader.load(df)


def load_codpayment_data(df: pd.DataFrame) -> None:
    """Load COD payment data"""
    loader = get_loader("codpayment")
    loader.load(df)


def load_confirmation_data(df: pd.DataFrame) -> None:
    """Load confirmation data"""
    loader = get_loader("confirmation")
    loader.load(df)


def load_tracker_data(df: pd.DataFrame) -> None:
    """Load tracker data"""
    loader = get_loader("tracker")
    loader.load(df)
