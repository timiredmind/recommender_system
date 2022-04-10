from flask_restful import Resource
from models.actor import Actor
from schemas import ActorSchema, PaginatedActorSchema
from webargs import fields
from webargs.flaskparser import use_kwargs
from http import HTTPStatus
from flask_jwt_extended import jwt_required
from extensions import limiter


class ActorCollectionResource(Resource):
    @jwt_required()
    @limiter.limit(limit_value="1/second", override_defaults=False)
    @use_kwargs(
        {"page": fields.Integer(missing=1),
         "per_page": fields.Integer(missing=10),
         "sort": fields.String(missing="name"),
         "order": fields.String(missing="asc"),
         "q": fields.String(missing="")
         },
        location="query"
    )
    def get(self, page, per_page, sort, order, q):
        search = f"%{q}%"
        if sort != "id":
            sort = "name"

        if order == "desc":
            sort_logic = getattr(Actor, sort).desc()
        else:
            sort_logic = getattr(Actor, sort).asc()
        actors = Actor.query.filter(
            Actor.name.ilike(search)).order_by(sort_logic).paginate(page=page, per_page=per_page)
        return PaginatedActorSchema().dump(actors), HTTPStatus.OK


class ActorResource(Resource):
    @jwt_required()
    @limiter.limit(limit_value="1/second", override_defaults=False)
    def get(self, actor_id):
        actor = Actor.query.filter_by(id=actor_id).first()
        if not actor:
            return {
                "msg": "Mesaage not found."
            }, HTTPStatus.OK

        return ActorSchema(exclude=("id", )).dump(actor), HTTPStatus.OK


