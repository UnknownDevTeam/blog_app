from flask import Blueprint, request, Response, jsonify, current_app
from function_jwt import write_token, validate_token
from bson import json_util
from json import dumps
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    db = current_app.config['db']
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
    except KeyError:
        return Response(dumps({"message":"Invalid key"}), 418, mimetype='application/json')

    if not email or not password:
        return Response(dumps({"message": "Incomplete fields"}), 400, mimetype='application/json')
    
    find_user = db.users.find_one({"email": email})
    
    if not find_user:
        return Response(dumps({"message": "Invalid credentials"}), 404, mimetype='application/json')
    elif not check_password_hash(find_user["password"], password):
        return Response(dumps({"message": "Invalid credentials"}), 404, mimetype='application/json')
    else:
        id = find_user["_id"]
        token = write_token(({"_id": str(id)}))
        return Response(token, 200)


@auth_bp.route('/sign-up', methods=['POST'])
def sign_up():
    db = current_app.config['db']
    try:
        data = request.get_json()
        name = data['name']
        user = data['user']
        email = data['email']
        password = data['password']
    
    except KeyError:
        return Response(dumps({"message":"Invalid key"}), 418, mimetype='application/json')

    find_user = db.users.find_one({"email" : email})

    if find_user is not None:
        return Response(dumps({"message": "Email already exists"}), 418, mimetype='application/json')

    find_user = db.users.find_one({"user" : user})

    if find_user is not None:
        return Response(dumps({"message": "User already exists"}), 418, mimetype='application/json')
    elif not name or not user or not email or not password:
        return Response(dumps({"message": "Incomplete fields"}), 418, mimetype='application/json')  
    elif  "@" not in email or "." not in email:
        return Response(dumps({"message": "Invalid email"}), 418, mimetype='application/json')
    elif len(password) < 8:
        return Response(dumps({"message": "Password must have at least 8 characters"}), 418, mimetype='application/json')
    else:
        password = generate_password_hash(password, method="sha256")
        new_user = db.users.insert_one({
                                     "name" : name,
                                     "user" : user,
                                     "email" : email,
                                     "password" : password})
        id = new_user.inserted_id
        token = write_token(({"_id": str(id)}))
        return Response(token, 201)


@auth_bp.route('/protected')
@validate_token
def protected():
    return Response(dumps({"message": "yep incoming, congratulations :)"}), 200, mimetype='application/json')