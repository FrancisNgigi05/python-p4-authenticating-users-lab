#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


# The login secion of the API
class Login(Resource):
    def post(self):
        data = request.get_json()
        # Confirming that the user is in the db
        user = User.query.filter(User.username == data['username']).first()
        # Giving the specific user the session
        session['user_id'] = user.id
        # Returning the users data after logging in
        return user.to_dict(), 200

# The logging section of the API    
class Logout(Resource):
    def delete(self): 
        # Removing the session that was assigned to a specific user
        session['user_id'] = None
        # Returning the logging out response to indicate the logging out is successfull
        return {}, 204

# This is the API section that makes sure that the user is logged in even after refreshing the page
class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        # Checking if that specific user was assigned a session
        if user:
            return user.to_dict(), 200
        else:
            return {}, 401

api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(port=5555, debug=True)