# models/mongodb/city.py

from mongoengine import Document, fields, EmbeddedDocument
import datetime


class City(Document):
    name = fields.StringField(required=True, unique=True)

    createdAt = fields.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = fields.DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        "ordering": ["-createdAt"],
    }

    def save(self, *args, **kwargs):
        # Update the 'updatedAt' field each time the document is saved
        self.updatedAt = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)
