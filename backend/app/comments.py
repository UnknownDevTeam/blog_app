from array import array
from contextlib import nullcontext
from function_jwt import validate_token, current_user
from flask import Blueprint, request, Response, current_app
from json import dumps
from bson import json_util, objectid
from datetime import datetime

comments_bp = Blueprint('comments', __name__, url_prefix='/comments')

@comments_bp.route('/<post_id>', methods=['GET','POST'])
@validate_token
def comment(post_id):
    db =  current_app.config['db']
    try:
        post = db.posts.find_one({"_id": objectid.ObjectId(f"{post_id}")})
        if str(json_util.dumps(post)) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')
    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            comment_data = data['comment']
        except KeyError:
            return Response(dumps({"message": "key error"}), 408, mimetype='application/json')

        date = datetime.now()
        user_id = current_user()['_id']

        try:
            db.comments.insert_one({"user_id" : objectid.ObjectId(f"{user_id}"),
                                    "post_id": objectid.ObjectId(f"{post_id}"),
                                    "type": "comment",
                                    "comment": f"{comment_data}",
                                    "date": f"{date}"})

            return Response(dumps({"message": "Comment created successfully"}), 201, mimetype='application/json')

        except:
            return Response(dumps({"message": "Error creating comment"}), 408, mimetype='application/json')
    
    comments = db.comments.find_one({"post_id" : objectid.ObjectId(f"{post_id}")})
    
    if str(json_util.dumps(comments)) == "null":
        return Response(dumps({"message": "No comments yet"}), 408, mimetype='application/json')
    else:
        comments = db.comments.find({"post_id" : objectid.ObjectId(f"{post_id}")})
        response = post, {"comments": comments}
        return Response(json_util.dumps(response), 408, mimetype='application/json')



@comments_bp.route('/reply/<type_id>', methods=['GET','POST'])
@validate_token
def reply(type_id):
    db =  current_app.config['db']
    try:
        type = db.comments.find_one({"_id": objectid.ObjectId(f"{type_id}")})
        if str(json_util.dumps(type)) == "null":
            return Response( dumps({"message": "That id is not found"}), 408, mimetype='application/json')
    except:
        return Response( dumps({"message": "Invalid id"}), 408, mimetype='application/json')
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            reply_data = data['reply']
        except KeyError:
            return Response(dumps({"message": "key error"}), 408, mimetype='application/json')

        date = datetime.now()
        user_id = current_user()['_id']

        if str(type["type"]) == "comment":
            db.comments.insert_one({"user_id" : objectid.ObjectId(f"{user_id}"),"comment_id": objectid.ObjectId(f"{type_id}"),"type": "reply","reply": f"{reply_data}","date": f"{date}"})
            return Response(dumps({"message": "Reply to comment created successfully"}), 201, mimetype='application/json')
        else:
            db.comments.insert_one({"user_id" : objectid.ObjectId(f"{user_id}"),"reply_id": objectid.ObjectId(f"{type_id}"),"type": "reply","reply": f"{reply_data}","date": f"{date}"})
            return Response(dumps({"message": "Reply to reply created successfully"}), 201, mimetype='application/json')
    
    type_data = str(type['type']) + "_id"

    reply = db.comments.find_one({type_data : objectid.ObjectId(f"{type_id}")})

    if str(json_util.dumps(reply)) == "null":
        return Response(dumps({"message": "No replies yet"}), 408, mimetype='application/json')
    else:
        reply = db.comments.find({type_data : objectid.ObjectId(f"{type_id}")})
        response = type, {"replies": reply}
        return Response(json_util.dumps(response), 408, mimetype='application/json')