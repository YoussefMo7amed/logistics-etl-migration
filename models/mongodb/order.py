# models/mongodb/order.py

from mongoengine import Document, EmbeddedDocument, fields
import datetime


from .city import City
from .zone import Zone


class Address(EmbeddedDocument):
    floor = fields.StringField()
    apartment = fields.StringField()
    secondLine = fields.StringField()
    city = fields.ReferenceField(City, required=True)
    zone = fields.ReferenceField(Zone, required=True)
    district = fields.StringField(required=True)
    firstLine = fields.StringField(required=True)
    geoLocation = fields.ListField(fields.FloatField(), required=True)
    country = fields.ReferenceField("Country")


class Cod(EmbeddedDocument):
    amount = fields.FloatField(required=True)
    isPaidBack = fields.BooleanField(required=True, default=False)
    collectedAmount = fields.FloatField(required=True)


class Confirmation(EmbeddedDocument):
    isConfirmed = fields.BooleanField(required=True)
    numberOfSmsTrials = fields.FloatField(required=True, default=0)


class Order(Document):
    cod = fields.EmbeddedDocumentField(Cod, required=True)
    collectedFromBusiness = fields.DateTimeField(required=True)
    confirmation = fields.EmbeddedDocumentField(Confirmation, required=True)
    createdAt = fields.DateTimeField(required=True)
    dropOffAddress = fields.EmbeddedDocumentField(Address, required=True)
    pickupAddress = fields.EmbeddedDocumentField(Address, required=True)
    receiver = fields.ReferenceField("Receiver", required=True)
    star = fields.ReferenceField("Star", required=True)
    tracker = fields.ReferenceField("Tracker", required=True)
    orderId = fields.StringField(required=True)
    type = fields.StringField(choices=["SEND", "OTHER"], required=True)
    updatedAt = fields.DateTimeField(required=True)
    createdAt = fields.DateTimeField(default=datetime.datetime.utcnow)
    meta = {
        "ordering": ["-createdAt"],  # Order by creation time, descending
    }

    def save(self, *args, **kwargs):
        # Update the 'updatedAt' field each time the document is saved
        self.updatedAt = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)
