from flask_restful import Resource
from models.genres import Genre
from schemas import GenreSchema, PaginatedGenreSchema
from http import HTTPStatus
from webargs import fields
from webargs.flaskparser import use_kwargs
from extensions import limiter
from flask_jwt_extended import jwt_required


class GenreCollectionResource(Resource):
    @jwt_required()
    @limiter.limit(limit_value="1/second", override_defaults=False)
    @use_kwargs({
        "page": fields.Integer(missing=1),
        "per_page": fields.Integer(missing=10),
        "sort": fields.String(missing="name"),
        "order": fields.String(missing="asc"),
        "q": fields.String(missing="")
    }, location="query")
    def get(self, page, per_page, sort, order, q):
        search = f"%{q}%"
        if sort != "id":
            sort = "name"
        if order == "desc":
            sort_logic = getattr(Genre, sort).desc()
        else:
            sort_logic = getattr(Genre, sort).asc()
        genres = Genre.query.filter(Genre.name.ilike(search)).order_by(sort_logic).paginate(page=page, per_page=per_page)
        return PaginatedGenreSchema().dump(genres), HTTPStatus.OK


class GenreResource(Resource):
    @limiter.limit(limit_value="1/second", override_defaults=False)
    def get(self, genre_id):
        genre = Genre.query.filter_by(id=genre_id).first()
        if not genre:
            return {
                "msg": "Genre not found."
            }, HTTPStatus.NOT_FOUND

        return GenreSchema(exclude=("id",)).dump(genre), HTTPStatus.OK
