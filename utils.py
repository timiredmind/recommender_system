from passlib.hash import bcrypt
from flask import request
from urllib.parse import urlencode


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def get_url(page):
    # Return query_args as regular dict instead of multidict
    query_args = request.args.to_dict()
    query_args["page"] = page

    return f"{request.base_url}?{urlencode(query_args)}"





