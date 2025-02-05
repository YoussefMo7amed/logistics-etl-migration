# models/mongodb/country.py

from mongoengine import Document, fields
import datetime


class Country(Document):
    name = fields.StringField(required=True)
    code = fields.StringField(required=True)
    
    createdAt = fields.DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = fields.DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        "ordering": ["-createdAt"],  # Order by creation time, descending
    }

    def save(self, *args, **kwargs):
        # Update the 'updatedAt' field each time the document is saved
        self.updatedAt = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)
