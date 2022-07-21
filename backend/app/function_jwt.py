from json import dumps
from flask import Response, request
from jwt import encode, decode, exceptions
from datetime import datetime, timedelta
from functools import wraps

def expire_date(days=15):
    now = datetime.now()
    exp = now + timedelta(days=days)
    return exp

def write_token(data: dict):
    password = "password"
    token = encode(payload={**data, "exp":expire_date()}, key=password, algorithm="HS256")
    return token.encode("UTF-8")


def validate_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = request.headers['Authorization']
            if not token:
                raise KeyError
            token = token.split(" ")[1]
            decode(token, key="password", algorithms=["HS256"])
            return func(*args, **kwargs) 
        except exceptions.DecodeError:
            return Response(dumps({"message" : "invalid token"}), 401)
        except exceptions.ExpiredSignatureError:
            return Response(dumps({"message" : "token expired"}), 401)       
        except KeyError:
            return Response(dumps({
                "status": "error",
                "message": "There's no Authorization header in the request."
            }), 400)
    return wrapper
            