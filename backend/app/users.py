from flask import Blueprint, Response, request, current_app
from function_jwt import validate_token, current_user
from json import dumps
from bson import json_util, objectid
from werkzeug.security import check_password_hash, generate_password_hash

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/profile', methods={'GET','PUT'})
@validate_token
def my_profile():
    db =  current_app.config['db']
    id = current_user()['_id']
    name = current_user()['name']
    user = current_user()['user']
    email = current_user()['email']
        
    if request.method  == 'PUT':
        password = current_user()['password']
        try:
            data = request.get_json()
            new_name = data['name']
            new_user = data['user']                   
        except KeyError:
            return Response(dumps({"message":"Invalid key"}), 418, mimetype='application/json')
        
        try:
            new_email = data['email']
            new_password = data['password']
            if new_email != email:
                return Response(dumps({"message":"Email and password don't change here"}), 418, mimetype='application/json')
            elif not check_password_hash(password, new_password):
                return Response(dumps({"message":"Email and password don't change here"}), 418, mimetype='application/json')
            else:
                new_email = email
                new_password = password
        except KeyError:
            pass
        
        if not new_name or not new_user:
            return Response(dumps({"message":"Incomplete fields"}), 418, mimetype='application/json')
        if user != new_user:
            find_user = db.users.find_one({"user" : f"{new_user}"})
            find_user = json_util.dumps(find_user)
            if str(find_user) != "null":
                return Response(dumps({"message": "User already exists"}), 418, mimetype='application/json')

        try:
            db.users.update_one({"_id": objectid.ObjectId(f"{current_user()['_id']}")},{ "$set": { "name": f"{new_name}",
                                                                                                    "user": f"{new_user}",
                                                                                                    "email": f"{new_email}",
                                                                                                    "password": f"{new_password}" } })
                                                                                                    
            return Response(dumps({"message":"Data updated successful"}), 418, mimetype='application/json')

        except:
            return Response(dumps({"message":"Error updating data"}), 418, mimetype='application/json')
     
    response = {
        "name": name,
        "user": user,
        "email": email,
        "password": "********"
    }

    return Response(dumps(response), 200, mimetype='application/json')


@users_bp.route('/change-password', methods={'PUT'})
@validate_token
def change_password():
    db =  current_app.config['db']
    name = current_user()['name']
    user = current_user()['user']
    email = current_user()['email']
    password = current_user()['password']
    try:
        data = request.get_json()
        old_password = data['old_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']

    except KeyError:
        return Response(dumps({"message":"Invalid key"}), 418, mimetype='application/json')


    if not old_password or not new_password or not confirm_password:
        return Response(dumps({"message":"Incomplete fields"}), 418, mimetype='application/json')
    elif not check_password_hash(password, old_password):
        return Response(dumps({"message":"Incorrect password"}), 418, mimetype='application/json')
    elif old_password == new_password:
        return Response(dumps({"message":"The password is the same"}), 418, mimetype='application/json')
    elif new_password != confirm_password:
        return Response(dumps({"message":"Passwords don't match"}), 418, mimetype='application/json')
    elif len(new_password) < 8:
        return Response(dumps({"message":"Password must have at least 8 characters"}), 418, mimetype='application/json')
    else:
        password = generate_password_hash(new_password, method="sha256")
        db.users.update_one({"_id": objectid.ObjectId(f"{current_user()['_id']}")},{ "$set": { "name": f"{name}",
                                                                                                    "user": f"{user}",
                                                                                                    "email": f"{email}",
                                                                                                    "password": f"{password}" } })
        return Response(dumps({"message":"Password updated successful"}), 200, mimetype='application/json')