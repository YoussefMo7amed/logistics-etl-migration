import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the system path to import models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# from connections.mongo_connector import get_mongo_client
from models.mongodb.city import City
from models.mongodb.zone import Zone
from models.mongodb.country import Country
from models.mongodb.receiver import Receiver
from models.mongodb.star import Star
from models.mongodb.tracker import Tracker
from models.mongodb.order import Order, Address

from mongoengine import connect
from config.settings import MONGO_URI


def generate_random_name():
    first_names = [
        "Ahmed",
        "Omar",
        "Youssef",
        "Karim",
        "Mohamed",
        "Ali",
        "Hassan",
        "Ibrahim",
        "Mahmoud",
        "Khaled",
        "Amr",
        "Mostafa",
        "Ayman",
        "Ashraf",
        "Hossam",
        "Sherif",
        "Waleed",
        "Tamer",
        "Sameh",
        "Ramy",
    ]
    last_names = [
        "Hesham",
        "Mostafa",
        "Khaled",
        "Mahmoud",
        "Saeed",
        "Gamal",
        "Tarek",
        "Samir",
        "Mahmoud",
        "Khaled",
        "Amr",
        "Mostafa",
        "Ayman",
        "Ashraf",
        "Hossam",
        "Sherif",
        "Waleed",
        "Tamer",
        "Sameh",
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_random_city():
    cities = [
        "Cairo",
        "Alexandria",
        "Giza",
        "Luxor",
        "Aswan",
        "Mansoura",
        "Suez",
        "Hurghada",
        "Port Said",
        "Damietta",
        "Ismailia",
        "Faiyum",
        "Zagazig",
        "Asyut",
        "Sohag",
        "Tanta",
        "Minya",
        "Qena",
        "Beni Suef",
        "Damanhur",
    ]
    return random.choice(cities)


def get_or_create_country(country_name, code):
    country = Country.objects(name=country_name, code=code).first()
    if not country:
        country = Country(name="Egypt", code="EG").save()
    return country


def get_or_create_city(city_name):
    city = City.objects(name=city_name).first()
    if not city:
        city = City(name=city_name).save()
    return city


def get_or_create_zone(zone_name):
    zone = Zone.objects(name=zone_name).first()
    if not zone:
        zone = Zone(name=zone_name).save()
    return zone


def create_random_phone():
    return f"01{random.randint(0, 2)}{random.randint(100000000, 999999999)}"


def create_dummy_data(num_orders=10):
    # Connect to MongoDB
    client = connect(host=MONGO_URI)

    # Create example country
    country = get_or_create_country("Egypt", "EG")

    for i in range(num_orders):
        # Generate different city and zone
        city_name = generate_random_city()
        zone_name = f"Zone-{random.randint(1, 10)}"
        city = get_or_create_city(city_name)
        zone = get_or_create_zone(zone_name)

        # Create receiver and star with different names
        receiver = Receiver(
            firstName=generate_random_name().split()[0],
            lastName=generate_random_name().split()[1],
            phone=create_random_phone(),
        ).save()
        star = Star(name=generate_random_name(), phone=create_random_phone()).save()
        tracker = Tracker(orderId=f"4233895-{i}").save()

        # Create order data with embedded documents
        order_data = Order(
            cod={
                "amount": random.randint(300, 500),
                "isPaidBack": False,
                "collectedAmount": random.randint(300, 500),
            },
            collectedFromBusiness=datetime.now(),
            confirmation={"isConfirmed": False, "numberOfSmsTrials": 0},
            createdAt=datetime.now(),
            dropOffAddress=Address(
                secondLine=f"{city_name} - District {random.randint(1, 5)}",
                city=city,
                zone=zone,
                district=f"{city_name} District",
                firstLine=f"{city_name}, Egypt",
                geoLocation=[random.uniform(29.0, 32.0), random.uniform(25.0, 31.0)],
            ),
            pickupAddress=Address(
                floor=str(random.randint(1, 10)),
                apartment=str(random.randint(1, 50)),
                secondLine=f"{random.randint(10, 50)} Random Street, {city_name}",
                city=city,
                zone=zone,
                district=city_name,
                firstLine=f"{city_name}, {country.name}",
                geoLocation=[random.uniform(29.0, 32.0), random.uniform(25.0, 31.0)],
                country=country,
            ),
            receiver=receiver,
            star=star,
            tracker=tracker,
            orderId=f"4233895-{i}",
            type="SEND",
            updatedAt=datetime.now() + timedelta(random.randint(1, 15)),
        )

        # Save the order to the database
        order_data.save()
        print(
            f"Order {i + 1} saved with city {city_name} and receiver {receiver.firstName} {receiver.lastName}"
        )


if __name__ == "__main__":
    create_dummy_data(num_orders=10)  # Change the number of orders as needed
