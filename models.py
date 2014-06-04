from app import db
import datetime

class Massage(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    name = db.Column(db.String(50))
    offered = db.Column(db.Boolean())

    @property
    def serialize(self):
        return {
            "id": self.id,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "name": self.name,
            "offered": 1 if self.offered else 0,
        }
        
    @property
    def serialize_timestamp(self):
        return {
            "id": self.id,
            "start": int((self.start - datetime.datetime(1970, 1, 1)).total_seconds()),
            "end": int((self.end - datetime.datetime(1970, 1, 1)).total_seconds()),
            "name": self.name,
            "offered": 1 if self.offered else 0,
        }

