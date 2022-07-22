from function_jwt import validate_token, current_user
from flask import Blueprint, request, Response, current_app
from json import dumps
from bson import json_util, objectid

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
            db.posts.insert_one({"user_id" : objectid.ObjectId(f"{user_id}"),
                                "user" : f"{user}",
                                "title" : f"{title}",
                                "content" : f"{content}",
                                "likes": 0})

            return Response(dumps({"message":"Post created succesfully"}), 200, mimetype='application/json')

    db_posts = json_util.dumps(db.posts.find())
    if str(db_posts) == "[]":
        return Response(dumps({"message":"There are no posts"}), 200, mimetype='application/json')
    return Response(db_posts, 200, mimetype='application/json')

@posts_bp.route('/<post_id>', methods = ['GET'])
@validate_token
def find_post(post_id):
    db =  current_app.config['db']
    try:
        post = db.posts.find_one({"_id": objectid.ObjectId(f"{post_id}")})
        post = json_util.dumps(post)
        if str(post) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')
        return Response( post, 200, mimetype='application/json')

    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')


@posts_bp.route('/user-posts/<user_id>', methods = ['GET'])
@validate_token
def user_posts(user_id):
    db =  current_app.config['db']
    try:
        user = db.users.find_one({"_id": objectid.ObjectId(f"{user_id}")})
        user = json_util.dumps(user)
        if str(user) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')

        posts = db.posts.find({"user_id": objectid.ObjectId(f"{user_id}")})
        posts = json_util.dumps(posts)
        if str(posts) == "[]":
            return Response( dumps({"message": "No posts yet"}), 200, mimetype='application/json')
        return Response( posts, 200, mimetype='application/json')

    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')

@posts_bp.route('/my-posts/', methods = ['GET'])
@validate_token
def my_posts():
    db =  current_app.config['db']
    user_id = current_user()['_id']
    posts = db.posts.find({"user_id": objectid.ObjectId(f"{user_id}")})
    posts = json_util.dumps(posts)
    if str(posts) == "[]":
            return Response( dumps({"message": "No posts yet"}), 200, mimetype='application/json')
    return Response( posts, 200, mimetype='application/json')
