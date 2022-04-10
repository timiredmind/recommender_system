from extensions import db
from models.language import language_tags
from models.director import Director
from models.actor import actors_tag
from models.genres import genre_tag


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    year_release = db.Column(db.Integer)
    language = db.relationship("Language", secondary=language_tags, lazy="subquery",
                               backref=db.backref("movies", lazy=True))
    director_id = db.Column(db.Integer, db.ForeignKey(Director.id), nullable=False)
    run_time = db.Column(db.String, nullable=False)
    actors = db.relationship("Actor", secondary=actors_tag, lazy="subquery", back_populates="movies")
    genres = db.relationship("Genre", secondary=genre_tag, lazy="subquery", back_populates="movies")



