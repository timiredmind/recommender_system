from extensions import db

language_tags = db.Table("language_tags",
                         db.Column("language_id", db.Integer, db.ForeignKey("language.id"), primary_key=True),
                         db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True)
)


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)