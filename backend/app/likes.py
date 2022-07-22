from flask import Blueprint, current_app, Response
from function_jwt import validate_token, current_user
from bson import objectid, json_util
from datetime import datetime
from json import dumps

likes_bp = Blueprint('likes', __name__, url_prefix='/likes')

@likes_bp.route('/like_post/<post_id>')
@validate_token
def like_post(post_id):
    db =  current_app.config['db']
    try:
        post = db.posts.find_one({"_id": objectid.ObjectId(f"{post_id}")})
        if str(json_util.dumps(post)) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')
    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')
    
    user_id = current_user()["_id"]

    likes = db.likes.find_one({"user_id": objectid.ObjectId(f"{user_id}"), "post_id": objectid.ObjectId(f"{post_id}")})
    if str(json_util.dumps(likes)) == "null":
        db.likes.insert_one({"user_id": objectid.ObjectId(f"{user_id}"),
                            "post_id": objectid.ObjectId(f"{post_id}"),
                            "date": f"{datetime.now()}"})     
    else:
        return Response( dumps({"message": "You had already liked before"}), 408, mimetype='application/json')
        
    likes = post["likes"]
    likes += 1

    try:
        db.posts.update_one({"_id": objectid.ObjectId(f"{post_id}")},{ "$set": {"likes": likes } })

        return Response(dumps({"message":"You liked"}), 200, mimetype='application/json')

    except:
        return Response(dumps({"message":"Error giving like"}), 418, mimetype='application/json')

@likes_bp.route('/remove_post/<post_id>')
@validate_token
def remove_like_post(post_id):
    db =  current_app.config['db']
    try:
        post = db.posts.find_one({"_id": objectid.ObjectId(f"{post_id}")})
        if str(json_util.dumps(post)) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')
    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')
    
    user_id = current_user()["_id"]

    likes = db.likes.find_one({"user_id": objectid.ObjectId(f"{user_id}"), "post_id": objectid.ObjectId(f"{post_id}")})
    if str(json_util.dumps(likes)) != "null":
        db.likes.delete_one({"user_id": objectid.ObjectId(f"{user_id}")})     
    else:
        return Response( dumps({"message": "You had not liked this post"}), 408, mimetype='application/json')
        
    likes = post["likes"]
    try:
        likes -= 1
        db.posts.update_one({"_id": objectid.ObjectId(f"{post_id}")},{ "$set": {"likes": likes } })
        return Response(dumps({"message":"You remove a like post"}), 200, mimetype='application/json')
    except:
        return Response(dumps({"message":"Error removing like"}), 418, mimetype='application/json')




@likes_bp.route('/like_comment/<type_id>')
@validate_token
def like_comment(type_id):
    db =  current_app.config['db']
    try:
        type = db.comments.find_one({"_id": objectid.ObjectId(f"{type_id}")})
        if str(json_util.dumps(type)) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')
    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')
    
    user_id = current_user()["_id"]
    type_data = str(type['type']) + "_id"

    likes = db.likes.find_one({"user_id": objectid.ObjectId(f"{user_id}"), type_data: objectid.ObjectId(f"{type_id}")})
    if str(json_util.dumps(likes)) == "null":
        db.likes.insert_one({"user_id": objectid.ObjectId(f"{user_id}"),
                            type_data: objectid.ObjectId(f"{type_id}"),
                            "date": f"{datetime.now()}"})     
    else:
        return Response( dumps({"message": "You had already liked before"}), 408, mimetype='application/json')
        
    try:
        likes = type["likes"]
        likes += 1
    except:
        likes = 1

    
    try:
        db.comments.update_one({"_id": objectid.ObjectId(f"{type_id}")},{ "$set": {"likes": likes } })
        if type_data == "comment_id":
            return Response(dumps({"message":"You liked a comment"}), 200, mimetype='application/json')
        else:
            return Response(dumps({"message":"You liked a reply"}), 200, mimetype='application/json')

    except:
        return Response(dumps({"message":"Error giving like"}), 418, mimetype='application/json')






@likes_bp.route('/remove_comment/<type_id>')
@validate_token
def remove_like_comment(type_id):
    db =  current_app.config['db']
    try:
        type = db.comments.find_one({"_id": objectid.ObjectId(f"{type_id}")})
        if str(json_util.dumps(type)) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')
    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')
    
    user_id = current_user()["_id"]
    type_data = str(type["type"]) + "_id"

    likes = db.likes.find_one({"user_id": objectid.ObjectId(f"{user_id}"), type_data: objectid.ObjectId(f"{type_id}")})
    if str(json_util.dumps(likes)) != "null":
        db.likes.delete_one({"user_id": objectid.ObjectId(f"{user_id}")})     
    else:
        return Response( dumps({"message": "You had not liked this post"}), 408, mimetype='application/json')
        
    try:
        likes = type["likes"]
        likes -= 1
        db.comments.update_one({"_id": objectid.ObjectId(f"{type_id}")},{ "$set": {"likes": likes } })
        if type_data == "comment_id":
            return Response(dumps({"message":"You remove a comment like"}), 200, mimetype='application/json')
        else:
            return Response(dumps({"message":"You remove a reply like"}), 200, mimetype='application/json')
    except:
        return Response(dumps({"message":"Error removing like"}), 418, mimetype='application/json')





