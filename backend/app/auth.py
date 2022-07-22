from flask import Blueprint, request, Response, jsonify, current_app
from function_jwt import write_token, validate_token
from bson import json_util
from json import dumps
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
#db = current_app.config['db']

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
        return Response(dumps({"message": "Incomplete fields"}), 418, mimetype='application/json')
    
    find_user = db.users.find_one({"email": f"{email}"})
    test_user = json_util.dumps(find_user)
    if str(test_user) == "null":
        return Response(dumps({"message": "This email is not registered"}), 418, mimetype='application/json')
    elif not check_password_hash(find_user["password"], password):
        return Response(dumps({"message": "Incorrect password"}), 418, mimetype='application/json')
    else:
        id = find_user["_id"]
        token = write_token(({"_id": f"{id}"}))
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
        #return Response(jsonify({"message":"Invalid key"}), 418)
        return Response(dumps({"message":"Invalid key"}), 418, mimetype='application/json')

    find_user = db.users.find_one({"email" : f"{email}"})
    find_user = json_util.dumps(find_user)

    if str(find_user) != "null":
        return Response(dumps({"message": "Email already exists"}), 418, mimetype='application/json')

    find_user = db.users.find_one({"user" : f"{user}"})
    find_user = json_util.dumps(find_user)

    if str(find_user) != "null":
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
                                     "name" : f"{name}",
                                     "user" : f"{user}",
                                     "email" : f"{email}",
                                     "password" : f"{password}"})
        id = new_user.inserted_id
        token = write_token(({"_id": f"{id}"}))
        return Response(token, 201)



@auth_bp.route('/protected')
@validate_token
def protected():
    return Response(dumps({"message": "yep incoming, congratulations :)"}), 200, mimetype='application/json')