from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    DateTime,
    Boolean,
    Numeric,
    Index,
    Float,
)
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship, declarative_base
from geoalchemy2 import Geometry
from datetime import datetime

Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    mongo_id = Column(String(24), unique=True)
    name = Column(String(50), nullable=False)
    code = Column(String(2), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )


class City(Base):
    __tablename__ = "cities"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    mongo_id = Column(String(24), unique=True)
    name = Column(String(50), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )


class Zone(Base):
    __tablename__ = "zones"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    mongo_id = Column(String(24), unique=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )


class Address(Base):
    __tablename__ = "addresses"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    order_mongo_id = Column(String(24))
    first_line = Column(String(255))
    second_line = Column(String(255))
    district = Column(String(50))
    floor = Column(String(10))
    apartment = Column(String(10))
    geo_location = Column(Geometry("POINT", srid=4326))
    zone_id = Column(INTEGER(unsigned=True), ForeignKey("zones.id"))
    city_id = Column(INTEGER(unsigned=True), ForeignKey("cities.id"))
    country_id = Column(INTEGER(unsigned=True), ForeignKey("countries.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )
    type = Column(Enum("dropoff", "pickup"), nullable=False)
    zone = relationship("Zone")
    city = relationship("City")
    country = relationship("Country")

    __table_args__ = (
        Index("idx_addresses_geo", "geo_location", mysql_using="gist"),
        Index("idx_order_mongo_address_type", "order_mongo_id", "type", unique=True),
    )


class Receiver(Base):
    __tablename__ = "receivers"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    mongo_id = Column(String(24), unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )


class Star(Base):
    __tablename__ = "stars"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    mongo_id = Column(String(24), unique=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    mongo_id = Column(String(24), unique=True)
    order_number = Column(String(50), unique=True, nullable=False)
    type = Column(Enum("SEND", "RECEIVE", name="order_type"), nullable=False)
    pickup_address_id = Column(
        INTEGER(unsigned=True), ForeignKey("addresses.id"), nullable=False
    )
    dropoff_address_id = Column(
        INTEGER(unsigned=True), ForeignKey("addresses.id"), nullable=False
    )
    receiver_id = Column(
        INTEGER(unsigned=True), ForeignKey("receivers.id"), nullable=False
    )
    star_id = Column(INTEGER(unsigned=True), ForeignKey("stars.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )
    pickup_address = relationship("Address", foreign_keys=[pickup_address_id])
    dropoff_address = relationship("Address", foreign_keys=[dropoff_address_id])
    receiver = relationship("Receiver")
    star = relationship("Star")

    __table_args__ = (
        Index("idx_orders_receiver_id", "receiver_id"),
        Index("idx_orders_pickup_address_id", "pickup_address_id"),
        Index("idx_orders_dropoff_address_id", "dropoff_address_id"),
        Index("idx_orders_created_at", "created_at"),
        Index("idx_orders_updated_at", "updated_at"),
        Index("idx_orders_type", "type"),
    )


class CodPayment(Base):
    __tablename__ = "cod_payments"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    order_id = Column(INTEGER(unsigned=True), ForeignKey("orders.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    collected_amount = Column(Numeric(10, 2))
    is_paid_back = Column(Boolean, default=False)
    collected_from_business_at = Column(DateTime)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )

    order = relationship("Order")

    __table_args__ = (
        Index("idx_cod_payments_order_id", "order_id"),
        Index("idx_cod_payments_amount", "amount"),
    )


class Confirmation(Base):
    __tablename__ = "confirmations"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    order_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("orders.id"),
    )
    is_confirmed = Column(Boolean, default=False)
    number_of_sms_trials = Column(INTEGER(unsigned=True), default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )

    order = relationship("Order")

    __table_args__ = (Index("idx_confirmations_order_id", "order_id"),)


class Tracker(Base):
    __tablename__ = "trackers"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    mongo_id = Column(String(24), unique=True)
    order_id = Column(INTEGER(unsigned=True), ForeignKey("orders.id"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)

    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.now(datetime.timezone.utc),
    )

    order = relationship("Order")

    __table_args__ = (Index("idx_trackers_order_id", "order_id"),)
