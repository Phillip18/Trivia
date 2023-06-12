import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS, cross_origin
import random
import sys

sys.path.append('flaskr')
import models
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(db=0, test=False):
    # create and configure the app
    app = Flask(__name__)
    if (not test):
        with app.app_context():
            db = setup_db(app)
    # else db was be created in the test file
    
    CORS(app, resources = {r"/*": {"origins": "*"}})
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def categories():
        categories = db.session.query(Category).all()
        dictionary = {'categories': {}}
        dictionary['categories'] = {category.id: category.type for category in categories}
        db.session.close()
        return dictionary, 200
    
    @app.route('/questions')
    def questions():
        dictionary = {}
        # check if the page is given and that it's an integer
        if request.args.get('page') is None: abort(400)
        if not request.args.get('page').isdigit: abort(400)
        # get page
        page = int(request.args.get('page'))
        first = (page - 1) * QUESTIONS_PER_PAGE # question after which to start
        last = page * QUESTIONS_PER_PAGE # question with which to end
        questions = db.session.query(Question).slice(first, last).all()
        if questions == []: abort(422, 'Page out of range')
        total = db.session.query(Question).count()
        categories = db.session.query(Category).all()
        dictionary['questions'] = [question.format() for question in questions]
        dictionary['total_questions'] = total
        # list categories according to their ids
        dictionary['categories'] = {category.id: category.type for category in categories}
        dictionary['current_category'] = ''
        db.session.close()
        return dictionary, 200

    @app.route('/category', methods=['POST'])
    def questionsByCategory():
        data = request.json
        questions = [question.format() for question in db.session.query(Question).filter_by(category=data['category']).all()]
        if len(questions) == 0: abort(404, 'No questions in this category')
        dictionary = {
            'questions': questions,
            'total_questions': len(questions)
            }
        db.session.close()
        return jsonify(dictionary)

    @app.route('/question/<int:id>', methods=['DELETE'])
    def delete(id):
        question = db.session.query(Question).filter_by(id=id).first()
        if question == None: abort(422, 'No such question')
        db.session.delete(question)
        db.session.commit()
        db.session.close()
        return {}, 204

    @app.route('/question', methods=['POST'])
    def add():
            data = request.json
            db.session.add(Question(
                question = data['question'],
                answer = data['answer'],
                difficulty = data['difficulty'],
                category = data['category']
            ))
            db.session.commit()
            db.session.close()
            return {}, 201

    @app.route('/search', methods=['POST'])
    def search():
        searchTerm = request.json['searchTerm']
        questions = db.session.query(Question).filter(Question.question.ilike(f'%{searchTerm}%')).all()
        if questions == []: abort(404, 'No results')
        dictionary = {
            'questions': [question.format() for question in questions],
            'totalQuestions': len(questions),
            'currentCategory': ''
        }
        return jsonify(dictionary)

    @app.route('/quiz', methods=['POST'])
    def quiz():
            data = request.json
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']
            # get a random question that is not in the category spedcified
            if quiz_category == 0:
                question = db.session.query(Question).filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()    
            else:
                question = db.session.query(Question).filter(Question.category == quiz_category['id']).filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()
            db.session.close()
            if question is None:
                # return a question with flag value for the attribute "question"
                question = Question('none', '', '', 0) 
            return question.format() 

    # for testing
    @app.route('/error')
    def serverError():
        abort(500)

    @app.errorhandler(400)
    def badRequest(error):
        return jsonify({
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(404)
    def notFound(error):
        return jsonify({
            'message': error.description
        }), 404

    @app.errorhandler(422)
    def unprocessableRequest(error):
        return jsonify({
            'message': error.description
        }), 422

    @app.errorhandler(500)
    def internalServerError(error):
        db.session.rollback()
        return jsonify({
            'message': 'Internal Server Error'
        }), 500

    return app

