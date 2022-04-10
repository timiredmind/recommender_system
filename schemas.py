from marshmallow import fields, Schema
from utils import get_url

from passlib.hash import bcrypt


class UserSchema(Schema):
    class Meta:
        fields = ("username", "email", "password", "active", "date_created", "date_last_updated")
        ordered = True

    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Method(deserialize="generate_password_hash", load_only=True)
    active = fields.Boolean(dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    date_last_updated = fields.DateTime(dump_only=True)

    def generate_password_hash(self, password):
        return bcrypt.using(rounds=6).hash(password)


class PaginationSchema(Schema):
    class Meta:
        ordered = True

    links = fields.Method(serialize="generate_pagination_link")
    current_page = fields.Integer(dump_only=True, attribute="page")
    per_page = fields.Integer(dump_only=True)
    total_items = fields.Integer(attribute="total")
    total_pages = fields.Integer(attribute="pages")

    def generate_pagination_link(self, paginated_objects):
        links = {
            "first_page": get_url(1)
        }
        if paginated_objects.has_next:
            links["next_page"] = get_url(paginated_objects.next_num)
        if paginated_objects.has_prev:
            links["prev_page"] = get_url(paginated_objects.prev_num)
        if paginated_objects.pages == 0:
            links["last_page"] = get_url(1)
        else:
            links["last_page"] = get_url(paginated_objects.pages)

        return links


class MovieSchema(Schema):
    class Meta:
        fields = ["id", "name", "description", "year_release", "run_time", "_links", "director", "language", "actors",
                  "genres"]
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(data_key="movie_name")
    description = fields.String(required=True)
    year_release = fields.Integer(data_key="year_released", required=True)
    run_time = fields.String(required=True)
    _links = fields.Method("generate_links")
    director = fields.Nested("DirectorSchema", exclude=("id", "movies"))
    language = fields.Nested("LanguageSchema", many=True, data_key="languages")
    actors = fields.Nested("ActorSchema", many=True, exclude=("id", "movies"))
    genres = fields.Nested("GenreSchema", many=True, exclude=("id", "movies"))

    def generate_links(self, movie_object):
        links = dict()
        base_url = "http://127.0.0.1:5000"

        links["self"] = f"{base_url}/movies/{movie_object.id}"
        links["collection"] = f"{base_url}/movies"
        return links


class PaginatedMovieSchema(PaginationSchema):
    movies = fields.Nested("MovieSchema",only=("id", "name", "description"), many=True, attribute="items")


class DirectorSchema(Schema):
    class Meta:
        fields = ["id", "name", "_links", "movies"]
        ordered = True

    name = fields.String(data_key="directorName", required=True)
    _links = fields.Method("generate_links")
    movies = fields.Nested("MovieSchema", many=True, only=("name", "description", "_links"))

    def generate_links(self, director_object):
        links = dict()
        base_url = "http://127.0.0.1:5000"
        links["self"] = f"{base_url}/directors/{director_object.id}"
        links["collection"] = f"{base_url}/directors"
        return links


class PaginatedDirectorSchema(PaginationSchema):
    directors = fields.Nested("DirectorSchema", exclude=("id", "movies"), many=True, attribute="items")


class LanguageSchema(Schema):
    class Meta:
        fields = ["id", "name"]
        ordered = True

    name = fields.String(data_key="languageName")


class ActorSchema(Schema):
    class Meta:
        fields = ["id", "name", "_links", "movies"]
        ordered = True

    name = fields.String(required=True, data_key="actorName")
    _links = fields.Method("generate_links")
    movies = fields.Nested("MovieSchema", many=True, only=("name", "description", "_links"))

    def generate_links(self, actor_object):
        links = dict()
        base_url = "http://127.0.0.1:5000"
        links["self"] = f"{base_url}/actors/{actor_object.id}"
        links["collection"] = f"{base_url}/actors"
        return links


class PaginatedActorSchema(PaginationSchema):
    actors = fields.Nested("ActorSchema", exclude=("id", "movies"), attribute="items", many=True)


class GenreSchema(Schema):
    class Meta:
        fields = ["id", "name", "_links", "movies"]
        ordered = True

    name = fields.String(required=True, data_key="genreName")
    _links = fields.Method("generate_links")
    movies = fields.Nested("MovieSchema", many=True, only=("name", "description", "_links"))

    def generate_links(self, genre_object):
        links = dict()
        base_url = "http://127.0.0.1:5000"

        links["self"] = f"{base_url}/genres/{genre_object.id}"
        links["collection"] = f"{base_url}/genres"
        return links


class PaginatedGenreSchema(PaginationSchema):
    genre = fields.Nested("GenreSchema", exclude=("id", "movies"), many=True, attribute="items")

