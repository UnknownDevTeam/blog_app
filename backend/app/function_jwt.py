from json import dumps
from bson.objectid import ObjectId
from flask import Response, request, current_app
from jwt import encode, decode, exceptions
from datetime import datetime, timedelta
from functools import wraps
import config

def expire_date(days=15):
    now = datetime.now()
    exp = now + timedelta(days=days)
    return exp

def write_token(data: dict):
    password = current_app.config['SECRET_KEY']
    token = encode(payload={**data}, key=password, algorithm="HS256")
    return token.encode("UTF-8")


def validate_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = request.headers['Authorization']
            if not token:
                raise KeyError
            token = token.split(" ")[1]
            password = current_app.config['SECRET_KEY']
            decode(token, key=password, algorithms=["HS256"])
            return func(*args, **kwargs) 
        except exceptions.DecodeError:
            return Response(dumps({"message" : "invalid token"}), 401, mimetype='application/json')
        except exceptions.ExpiredSignatureError:
            return Response(dumps({"message" : "token expired"}), 401, mimetype='application/json')       
        except KeyError:
            return Response(dumps({
                "status": "error",
                "message": "There's no Authorization header in the request."
            }), 400, mimetype='application/json')
    return wrapper
            

def current_user():
    db =  current_app.config['db']
    token = request.headers['Authorization']
    token = token.split(" ")[1]
    password = current_app.config['SECRET_KEY']
    token_decode = decode(token, key=password, algorithms=["HS256"])
    try:
        user = db.users.find_one({"_id": ObjectId(token_decode['_id'])})
        return user
    except:
        Response(dumps({"message" : "toke error"}), 401, mimetype='application/json')
    