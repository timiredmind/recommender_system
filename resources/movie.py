from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.movie import Movie
from schemas import PaginatedMovieSchema, MovieSchema
from webargs import fields
from webargs.flaskparser import use_kwargs
from http import HTTPStatus
from sqlalchemy import or_, and_
from datetime import datetime
from extensions import limiter
from os import getenv
from services import get_similar_items, event_tracker


class MovieCollectionResource(Resource):
    @jwt_required()
    @limiter.limit(limit_value="1/second", override_defaults=False)
    @use_kwargs({
        "page": fields.Integer(missing=1),
        "per_page": fields.Integer(missing=10),
        "sort": fields.Str(missing="id"),
        "order": fields.Str(missing="asc"),
        "q": fields.Str(missing=""),
        "max_year": fields.Int(missing=datetime.now().year),
        "min_year": fields.Int(missing=1900)
    },
        location="query"
    )
    def get(self, page, per_page, sort, order, q, max_year, min_year):
        search = f"%{q}%"
        if sort not in ["id", "name", "year_release", "run_time"]:
            sort = "id"
        if order == "desc":
            sort_logic = getattr(Movie, sort).desc()
        else:
            sort_logic = getattr(Movie, sort).asc()
        movie_collection = Movie.query.filter(
            or_(Movie.name.ilike(search),
                Movie.description.ilike(search))).filter(
            and_(Movie.year_release >= min_year,
                 Movie.year_release <= max_year)).order_by(sort_logic).paginate(page=page, per_page=per_page)
        return PaginatedMovieSchema().dump(movie_collection), HTTPStatus.OK


class MovieResource(Resource):
    @jwt_required()
    @limiter.limit(limit_value="1/second", override_defaults=False)
    def get(self, movie_id):
        movie = Movie.query.filter_by(id=movie_id).first()
        if not movie:
            return {
                'msg': "Movie not found"
            }, HTTPStatus.NOT_FOUND

        event_tracker(user_id=get_jwt_identity(),
                      item_id=movie_id)

        recommendations = get_similar_items(campaignARN=getenv("SIMS_CAMPAIGN_ARN"), item_id=str(movie_id))
        recommendations = [Movie.query.get(item) for item in recommendations]
        return {"movie": MovieSchema().dump(movie),
                "recommendations": MovieSchema(many=True,
                                               only=("name", "description", "_links")
                                               ).dump(recommendations)}, HTTPStatus.OK




