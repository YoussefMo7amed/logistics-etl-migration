# models/mongodb/star.py

from mongoengine import Document, fields
import datetime


class Star(Document):
    name = fields.StringField(required=True)
    phone = fields.StringField(required=True)
    createdAt = fields.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = fields.DateTimeField(default=datetime.datetime.utcnow)
    meta = {
        "ordering": ["-createdAt"],  # Order by creation time, descending
    }

    def save(self, *args, **kwargs):
        # Update the 'updatedAt' field each time the document is saved
        self.updatedAt = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)
