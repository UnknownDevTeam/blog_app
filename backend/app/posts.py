from function_jwt import validate_token, current_user
from flask import Blueprint, request, Response, current_app
from json import dumps
from bson import json_util
from bson.objectid import ObjectId

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/', methods = ['GET', 'POST'])
@validate_token
def posts():
    db =  current_app.config['db']
    if request.method == 'POST':
        try:
            data = request.get_json()
            user_id = current_user()['_id']
            user = current_user()['user']
            title = data['title']
            content = data['content']
        
        except KeyError:
            return Response(dumps({"message":"Invalid key"}), 418, mimetype='application/json')

        if not title or not content:
            return Response(dumps({"message":"Incomplete fields"}), 418, mimetype='application/json')
        else:
            db.posts.insert_one({"user_id" : ObjectId(user_id),
                                "user" : user,
                                "title" : title,
                                "content" : content,
                                "likes": 0})

            return Response(dumps({"message":"Post created succesfully"}), 200, mimetype='application/json')

    db_posts = db.posts.find()
    posts_conv = str(json_util.dumps(db_posts))
    #if not posts:                  {aqui no funciona de esta manera, con el find_one si, pero aqui no y se necesita del find}
    if posts_conv == "[]":
        return Response(dumps({"message":"There are no posts"}), 200, mimetype='application/json')
    return Response(posts_conv, 200, mimetype='application/json')

@posts_bp.route('/<post_id>', methods = ['GET'])
@validate_token
def find_post(post_id):
    db =  current_app.config['db']
    try:
        post = db.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            return Response( dumps({"message": "That id is not found"}), 404, mimetype='application/json')
        return Response( json_util.dumps(post), 200, mimetype='application/json')

    except:
        return Response( dumps({"message": "Invalid id"}), 400, mimetype='application/json')


@posts_bp.route('/user-posts/<user_id>', methods = ['GET'])
@validate_token
def user_posts(user_id):
    db =  current_app.config['db']
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})

        if not user:
            return Response( dumps({"message": "That id is not found"}), 404, mimetype='application/json')

        posts = db.posts.find({"user_id": ObjectId(user_id)})
        posts_conv = str(json_util.dumps(posts))
        #if not posts:                  {aqui no funciona de esta manera, con el find_one si, pero aqui no y se necesita del find}
        if posts_conv == "[]":
            return Response( dumps({"message": "No posts yet"}), 404, mimetype='application/json')
        return Response( posts_conv, 200, mimetype='application/json')

    except:
        return Response( dumps({"message": "Invalid id"}), 400, mimetype='application/json')

@posts_bp.route('/my-posts/', methods = ['GET'])
@validate_token
def my_posts():
    db =  current_app.config['db']
    user_id = current_user()['_id']
    posts = db.posts.find({"user_id": ObjectId(user_id)})
    posts_conv = str(json_util.dumps(posts))
    #if not posts:                  {aqui no funciona de esta manera, con el find_one si, pero aqui no y se necesita del find, yo creo que es porque en vez de devolver el solo el dato como en el find_one, devuelve una [] vacia, pero no lo reconoce como un none, tambien intente con sin el str y tampoco}
    if posts_conv == "[]":
            return Response( dumps({"message": "No posts yet"}), 404, mimetype='application/json')
    return Response( posts_conv, 200, mimetype='application/json')
