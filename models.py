from app import db

class Massage(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    name = db.Column(db.String(50))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "name": self.name,
        }

