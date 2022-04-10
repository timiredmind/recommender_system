from flask_restful import Resource
from flask import request
from models.user import User
from models.movie import Movie
from models.token_blocklist import TokenBlocklist
from http import HTTPStatus
from utils import verify_password
from extensions import db, jwt
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from schemas import UserSchema
from schemas import MovieSchema
from os import getenv
from services import get_recommendations_for_user



# Check if JWT has been revoked
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.query.filter_by(jti=jti).scalar()
    return token is not None


class CreateUserResource(Resource):
    def post(self):
        user_info = request.get_json()
        # Validate users input
        try:
            deserialized_data = UserSchema().load(user_info)
        except ValidationError as errors:
            return {"msg": "Validation Error",
                    "errors": [errors.messages]}, HTTPStatus.BAD_REQUEST
        username = deserialized_data.get("username")
        email = deserialized_data.get("email")
        password = deserialized_data.get("password")

        if User.get_by_username(username):
            return {"msg": "Username already exists."}, HTTPStatus.CONFLICT

        if User.get_by_email(email):
            return {"msg": "Email address already registered to an existing user."}, HTTPStatus.CONFLICT

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=new_user.id)
        return {"access_token": access_token}, HTTPStatus.CREATED


class UserLoginResource(Resource):
    def post(self):
        login_details = request.get_json()
        try:
            UserSchema(only=["username", "password"]).load(login_details)
        except ValidationError as errors:
            return {"msg": "Validation Error",
                    "errors": [errors.messages]}, HTTPStatus.BAD_REQUEST

        username = login_details.get("username")
        password = login_details.get("password")
        user = User.get_by_username(username=username)
        if not user or not verify_password(password, user.password) or user.active is False:
            return {"msg": "Invalid username and password"}, HTTPStatus.BAD_REQUEST

        access_token = create_access_token(identity=user.id)

        return {"access_token": access_token}, HTTPStatus.OK


class UserExploreResource(Resource):
    @jwt_required()
    def get(self):

        recommendations = get_recommendations_for_user(campaignARN=getenv("CAMPAIGN_ARN"),
                                     user_id=str(get_jwt_identity()))
        recommendations = [Movie.query.get(item) for item in recommendations]

        return {"recommendations": MovieSchema(many=True, only=("name", "description", "_links")).dump(recommendations)
                }, HTTPStatus.OK


class UserLogOutResource(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        token = TokenBlocklist(jti=jti, user_id=user_id)
        db.session.add(token)
        db.session.commit()
        return {"msg": "You have logged out successfully."}, HTTPStatus.OK


class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        return UserSchema().dump(user), HTTPStatus.OK

    @jwt_required()
    def patch(self):
        json_data = request.get_json()
        try:
            UserSchema(partial=True, only=['username', "email"]).load(json_data)
        except ValidationError as errors:
            return {"msg": "Validation Error",
                    "errors": [errors.messages]}, HTTPStatus.BAD_REQUEST

        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        username = json_data.get("username")
        email = json_data.get("email")

        user.username = username or user.username
        user.email = email or user.email
        db.session.commit()
        return UserSchema().dump(user), HTTPStatus.OK

    def delete(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        user.active = False
        db.session.commit()
        return {}, HTTPStatus.NO_CONTENT

