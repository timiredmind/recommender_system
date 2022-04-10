from flask_restful import Resource
from models.director import Director
from schemas import DirectorSchema, PaginatedDirectorSchema
from http import HTTPStatus
from webargs import fields
from webargs.flaskparser import use_kwargs
from flask_jwt_extended import jwt_required
from extensions import limiter


class DirectorCollectionResource(Resource):
    @jwt_required()
    @limiter.limit(limit_value="1/seconds", override_defaults=False)
    @use_kwargs({
        "page": fields.Integer(missing=1),
        "per_page": fields.Integer(missing=10),
        "sort": fields.String(missing="name"),
        "order": fields.String(missing="asc"),
        "q": fields.String(missing="")
    }, location="query")
    def get(self, page, per_page, sort, order, q):
        search = f"%{q}%"
        if sort not in ["id", "name"]:
            sort = "name"

        if order == "desc":
            sort_logic = getattr(Director, sort).desc()
        else:
            sort_logic = getattr(Director, sort).asc()

        directors = Director.query.filter(Director.name.ilike(search)).order_by(sort_logic).paginate(page=page, per_page=per_page)
        return PaginatedDirectorSchema().dump(directors), HTTPStatus.OK


class DirectorResource(Resource):
    @jwt_required()
    @limiter.limit(limit_value="1/second", override_defaults=False)
    def get(self, director_id):
        director = Director.query.filter_by(id=director_id).first()
        if not director:
            return {"msg": "Director not found"}, HTTPStatus.NOT_FOUND

        return DirectorSchema(exclude=("id", )).dump(director), HTTPStatus.OK


