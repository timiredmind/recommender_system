from flask import Flask, request
from extensions import db, migrate, jwt, limiter
from config import Config
from flask_restful import Api
from resources.user import CreateUserResource, UserLoginResource, UserLogOutResource, UserProfileResource, UserExploreResource
from resources.movie import MovieCollectionResource, MovieResource
from resources.director import DirectorCollectionResource, DirectorResource
from resources.actor import ActorCollectionResource, ActorResource
from resources.genre import GenreCollectionResource, GenreResource


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)


def register_resources(app):
    api = Api(app)
    api.add_resource(CreateUserResource, "/register")
    api.add_resource(UserLoginResource, "/login")
    api.add_resource(UserLogOutResource, "/logout")
    api.add_resource(UserProfileResource, "/profile")
    api.add_resource(UserExploreResource, "/explore")
    api.add_resource(MovieCollectionResource, "/movies")
    api.add_resource(MovieResource, "/movies/<int:movie_id>")
    api.add_resource(DirectorCollectionResource, "/directors")
    api.add_resource(DirectorResource, "/directors/<int:director_id>")
    api.add_resource(ActorCollectionResource, "/actors")
    api.add_resource(ActorResource, "/actors/<int:actor_id>")
    api.add_resource(GenreCollectionResource, "/genres")
    api.add_resource(GenreResource, "/genres/<int:genre_id>")


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)
    register_extensions(app=app)
    register_resources(app=app)
    return app



@limiter.request_filter
def ip_whitelist():
    return request.remote_addr == "127.0.0.1"


if __name__ == '__main__':
    app = create_app(Config)
    app.run()
