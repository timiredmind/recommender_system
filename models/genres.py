from extensions import db

genre_tag = db.Table("genre_tag",
                     db.Column("genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True),
                     db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True)
)


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True, unique=True)
    movies = db.relationship("Movie", secondary=genre_tag, lazy="subquery", back_populates="genres")

