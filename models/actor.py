from extensions import db

actors_tag = db.Table("actors_tags",
                      db.Column("actor_id", db.Integer, db.ForeignKey("actors.id"), primary_key=True),
                      db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True)
)


class Actor(db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    movies = db.relationship("Movie", secondary=actors_tag, lazy="subquery", back_populates="actors")


def sidebar_data():
    top_tags = db.session.query(Actor,
                                db.func.count(actors_tag)
                                )

