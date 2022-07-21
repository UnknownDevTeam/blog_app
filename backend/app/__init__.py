from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, support_credentials=True)
    import config
    app.config.from_object(config)
    app.config['db'] = PyMongo(app).db
    
    import auth
    app.register_blueprint(auth.auth_bp)
    
    import posts
    app.register_blueprint(posts.posts_bp)
    
    import comments
    app.register_blueprint(comments.comments_bp)
    
    import users
    app.register_blueprint(users.users_bp)
    
    import likes
    app.register_blueprint(likes.likes_bp)
            
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'])
