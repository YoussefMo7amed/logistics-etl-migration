import mysql.connector
from sqlalchemy import create_engine, text
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging
from config.settings import SQL_CONFIG
from models.sql.sql_models import Base

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""

    pass


class MySQLConnector:
    """Handles MySQL database connections and operations."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MySQL connector with configuration.

        Args:
            config: Dictionary containing database configuration parameters
        """
        self.config = config
        self.engine = None

    def _create_database(self) -> None:
        """
        Creates the database if it doesn't exist.

        Raises:
            DatabaseConnectionError: If database creation fails
        """
        config_without_db = self.config.copy()
        config_without_db.pop("database", None)

        try:
            with mysql.connector.connect(**config_without_db) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS {self.config['database']}"
                    )
        except mysql.connector.Error as e:
            logger.error(f"Failed to create database: {e}")
            raise DatabaseConnectionError(f"Database creation failed: {e}")

    def _get_connection_string(self) -> str:
        """
        Builds and returns the SQLAlchemy connection string.

        Returns:
            str: SQLAlchemy connection string
        """
        return (
            f"mysql+mysqlconnector://"
            f"{self.config['user']}:{self.config['password']}"
            f"@{self.config['host']}/{self.config['database']}"
        )

    def _initialize_engine(self) -> None:
        """
        Initializes the SQLAlchemy engine with proper configuration.

        Raises:
            DatabaseConnectionError: If engine initialization fails
        """
        try:
            self.engine = create_engine(
                self._get_connection_string(),
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
            )
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise DatabaseConnectionError(f"Engine initialization failed: {e}")

    def _create_tables(self) -> None:
        """
        Creates all tables defined in the Base metadata if they don't exist.
        Skips if tables are already created.
        """
        try:
            Base.metadata.create_all(self.engine, checkfirst=True)
        except Exception as e:
            logger.warning(f"Table creation skipped, tables may already exist: {e}")

    def _test_connection(self) -> None:
        """
        Tests the database connection by executing a simple query.

        Raises:
            DatabaseConnectionError: If connection test fails
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            raise DatabaseConnectionError(f"Connection test failed: {e}")

    def initialize(self) -> Optional["MySQLConnector"]:
        """
        Initializes the database connection and performs all necessary setup.

        Returns:
            MySQLConnector: Self reference if successful, None if failed
        """
        try:
            self._create_database()
            self._initialize_engine()
            self._create_tables()
            self._test_connection()
            logger.info("Successfully connected to MySQL database via SQLAlchemy")
            return self
        except DatabaseConnectionError as e:
            logger.error(f"Database initialization failed: {e}")
            return None

    @contextmanager
    def get_engine(self):
        """
        Context manager for safely accessing the database engine.

        Yields:
            SQLAlchemy engine instance

        Raises:
            DatabaseConnectionError: If engine is not initialized
        """
        if not self.engine:
            raise DatabaseConnectionError("Database engine not initialized")
        try:
            yield self.engine
        except Exception as e:
            logger.error(f"Error during engine usage: {e}")
            raise


def get_mysql_engine():
    """
    Factory function to create and initialize MySQL connection.

    Returns:
        SQLAlchemy engine instance or None if initialization fails
    """
    connector = MySQLConnector(SQL_CONFIG)
    initialized_connector = connector.initialize()

    if initialized_connector:
        return initialized_connector.engine
    return None
