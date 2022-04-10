from extensions import db


class Director(db.Model):
    __tablename__ = "directors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    movies = db.relationship("Movie", backref="director", lazy=True)

