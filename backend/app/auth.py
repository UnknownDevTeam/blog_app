from flask import Blueprint, request, Response, jsonify, current_app
from function_jwt import write_token, validate_token
from bson import json_util
from json import dumps

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
        return Response(dumps({"message":"Invalid key"}), 418)

    if not email or not password:
        return Response(dumps({"message": "Incomplete fields"}), 418)
    
    find_user = db.users.find_one({"email": f"{email}"})
    test_user = json_util.dumps(find_user)
    if str(test_user) == "null":
        return Response(dumps({"message": "This email is not registered"}), 418)
    
    find_password = db.users.find_one({"email": f"{email}", "password": f"{password}"})
    test_password = json_util.dumps(find_password)
    if str(test_password) == "null":
        return Response(dumps({"message": "Incorrect password"}), 418)
    else:
        id = find_password["_id"]
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
        return Response(dumps({"message":"Invalid key"}), 418)

    find_user = db.users.find_one({"email" : f"{email}"})
    find_user = json_util.dumps(find_user)

    if str(find_user) != "null":
        return Response(dumps({"message": "User exist"}), 418)
    elif not name or not user or not email or not password:
        return Response(dumps({"message": "Incomplete fields"}), 418)  
    elif  "@" not in email or "." not in email:
        return Response(dumps({"message": "Invalid email"}), 418)
    elif len(password) < 8:
        return Response(dumps({"message": "Invalid password"}), 418)
    else:
        new_user = db.users.insert_one({
                                     "name" : f"{name}",
                                     "user" : f"{user}",
                                     "email" : f"{email}",
                                     "password" : f"{password}"})
        id = new_user.inserted_id
        token = write_token(({"_id": f"{id}"}))
        return Response(token, 200)



@auth_bp.route('/protected')
@validate_token
def protected():
    return Response(dumps({"message": "yep incoming, congratulations :)"}), 200)