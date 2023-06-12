import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        
        self.db = SQLAlchemy()
        self.database_name = os.environ.get('TEST_DATABASE_NAME')
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        
        # The value for the second argument in create_app function, True,
        # means that it's test mode, so database will not be created in the function
        # since it has been already created in this file
        self.app = create_app(self.db, True)
        
        self.app.config['SQLALCHEMY_DATABASE_URI'] = self.database_path
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.client = self.app.test_client()
        
        # binds the app to the current context
        with self.app.app_context():
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_categories(self):
        response = self.client.get('/categories')
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        
    def test_questions_valid_data_page_1(self):
        self.check(self.client.get('/questions?page=1'))
        
    def test_questions_valid_data_page_2(self):
        self.check(self.client.get('/questions?page=2'))

    def check(self, response):
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], '')

    def test_questions_invalid_query(self):
        response = self.client.get('/questions?invalid')
        data = response.json
        self.assertEqual(data['message'], 'Bad Request')
    
    def test_questions_page_out_of_range(self):
        response = self.client.get('questions?page=1000')
        data = response.json
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['message'], 'Page out of range')

    def test_questions_by_category(self):
        response = self.client.post('/category', json = {'category': 1})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_questions_by_category_no_questions(self):
        response = self.client.post('/category', json = {'category': 1000})
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'No questions in this category')

    def test_delete(self):
        with self.app.app_context():
            # first add question for deletion
            self.db.session.add(Question(
                    question = 'question for deleting',
                    answer = 'answer',
                    difficulty = 1,
                    category  = 1
                ))
            self.db.session.commit()
            
            # delete it
            question = self.db.session.query(Question).filter_by(question='question for deleting').first()
            id = question.id

            # check that response code is 204
            response = self.client.delete(f'question/{id}')
            self.assertEqual(response.status_code, 204)

            # check that the question is not in the database
            question = self.db.session.query(Question).filter_by(question='question for deleting').first()
            self.assertFalse(question)

    def test_delete_422(self):
        response = self.client.delete('question/1000')
        data = response.json
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['message'], 'No such question')

    def test_add_question(self):
        # add question
        response = self.client.post('/question', json = {
            'question': 'question for adding',
            'answer': 'answer',
            'difficulty': 1,
            'category': 1
        })

        # check that the code is 201
        self.assertEqual(response.status_code, 201)

        with self.app.app_context():
            # check that the question is in the database
            question = self.db.session.query(Question).filter_by(question = 'question for adding').first()
            self.assertEqual(question.question, 'question for adding')
            self.assertEqual(question.answer, 'answer')
            self.assertEqual(question.difficulty, 1)
            self.assertEqual(question.category, 1)
            
            # now delete it so that next time it would be
            # in the database only if it is successfully added
            self.db.session.delete(question)
            self.db.session.commit()

    def test_search(self):
        response = self.client.post('search', json = {'searchTerm': 'whaT is'})
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['questions'][1]['question'], 'What is the heaviest organ in the human body?')
        self.assertEqual(data['questions'][0]['question'], 'What is the largest lake in Africa?')

    def test_search_no_results(self):
        response = self.client.post('search', json = {'searchTerm': '!@#$'})
        data = response.json
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'No results')

    def test_questions_server_error(self):
        response = self.client.get('/error')
        data = response.json
        self.assertEqual(data['message'], 'Internal Server Error')

    def test_quiz_questions_from_a_category(self):
        # get questions from the category of science
        with self.app.app_context():
            questions = self.db.session.query(Question).filter_by(category=1).all()
        # submit request with two of the questions as previous ones
        response = self.client.post('/quiz', json = {
            'previous_questions': [questions[0].id, questions[1].id],
            'quiz_category': {
                'type': 'science',
                'id': 1
                }
        })
        self.assertEqual(response.status_code, 200)
        data = response.json
        # check that the questions do not include previous questions
        # (this is not yet a proof that the exclusion of prevoius questions
        # works, but this test is mostly designed to just check whether the
        # function gives out quiz questions)
        self.assertNotEqual(data['question'], questions[0].question)
        self.assertNotEqual(data['question'], questions[1].question)

    def test_quiz_questions_from_all_questions(self):
            # get questions
            with self.app.app_context():
                questions = self.db.session.query(Question).all()
            # submit request with two of the questions as previous ones
            # and with data that corresponds to clicking "All" for categories
            response = self.client.post('/quiz', json = {
                'previous_questions': [questions[0].id, questions[1].id],
                'quiz_category': {
                    'type': 'click',
                    'id': 0
                    }
            })
            self.assertEqual(response.status_code, 200)
            data = response.json
            # check that the questions do not include previous questions
            # (this is not yet a proof that the exclusion of prevoius questions
            # works, but this test is mostly designed to just check whether the
            # function gives out quiz questions)
            self.assertNotEqual(data['question'], questions[0].question)
            self.assertNotEqual(data['question'], questions[1].question)

    def test_quiz_no_questions(self):
        # get question from the category of science
        with self.app.app_context():
            questions = self.db.session.query(Question).filter_by(category=1).all()
        # submit request with all the science questions as previous ones
        response = self.client.post('/quiz', json = {
            'previous_questions': [questions[0].id, questions[1].id, questions[2].id],
            'quiz_category': {
                'type': 'science',
                'id': 1
                }
        })
        self.assertEqual(response.status_code, 200)
        # check that no questions are returned
        # (which is the proof that the function does not give out previous questions)
        self.assertEqual(response.json['question'], 'none')

    def test_500(self):
        data = self.client.get('/error').json
        self.assertEqual(data['message'],'Internal Server Error')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()