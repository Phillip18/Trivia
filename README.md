# Trivia App

This website lets you play the game of answering trivia questions.  

## Tools Needed
* Python 3.11 (other versions may work, too)  
* PostgreSQL 14.7 (other versions may work, too)

## Getting Started

1. Install dependencies
```
pip install -r requirements.txt
```

2. Set up the database  
In the backend directory:  
```
createdb trivia
psql trivia < trivia.psql
```
3. Change credentials for the database in the app  

In the .dotenv file, change the USERNAME and PASSWORD variables to the username and password of the owner of the resulting 'trivia' database (or of a user to whom you give all privileges for the database and all its tables).

4. Start the server  
In the backend directory:
```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

## Front End
Use port 3000.

## Testing
In the backend directory:
```
createdb test_trivia
psql test_trivia < trivia.psql
python test_flaskr.py
```
# API Documentation

This API lets one make requests to the server to get questions and play a question-answer game.

## Getting Started  
+ Base URL:  This project can be run only locally.  The server is set up to run at the default host 5000.  
+ Authentication: This app does not require authentication or an API key.  

## Error Handling
Error response object has a "status" number that corresponds to the type of error and a JSON object: {  'message': [message explaining the error]  }.  
The API will return four types of error: 400, 404, 422, and 500. However, returned messages for a given error type may vary.  
If there are no questions to be returned, 404 is returned with a message indicating that there are no questions.

## Endpoints

### GET /categories
Returns:  
* the list of categories  
* success status (true)  

Sample: curl http://localhost:5000/categories  
```{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

### GET /questions?page={page number}
Returns: 
* the list of categories 
* questions in all the categories at once, but only the part of questions that is on the indicated page of the list, 10 questions per page (the back end does not support a request for an unpaginated list)  
* current category (which is always "", since there is no current category in this case, but it is required in the rubric of Udacity)  
* total number of questions

Sample:  curl "http://localhost:5000/questions?page=1"
```
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": "",
  "questions": [
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    },
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Lake Victoria",
      "category": 3,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": 3,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    },
    {
      "answer": "Agra",
      "category": 3,
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    },
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }
  ],
  "total_questions": 18
}
```
### POST /category  
Accepts as payload: {"category": {category id}}  
Returns:  
* list of questions for the category with the given category id
* success status (true)
* number of questions returned 

Sample: curl http://localhost:5000/category -X POST -H "Content-Type: application/json" -d '{"category":2}'  
```
{
  "questions": [
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    },
    {
      "answer": "Mona Lisa",
      "category": 2,
      "difficulty": 3,
      "id": 17,
      "question": "La Giaconda is better known as what?"
    },
    {
      "answer": "One",
      "category": 2,
      "difficulty": 4,
      "id": 18,
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    },
    {
      "answer": "Jackson Pollock",
      "category": 2,
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ],
  "total_questions": 4
}
```
### DELETE /question/{question_id}  
Returns:  nothing (status code is 204)  
Sample: curl http://localhost:5000/question/21 -X DELETE  
There is no response JSON.

### POST /question  
Accepts as payload:  
```
    {
        question: {question},
        answer: {answer},
        difficulty: {difficulty number},
        category: {catogory id}
    }
```
Returns: nothing (status code is 201)  
Sample: curl http://localhost:5000/question -X POST -H "Content-Type: application/json" -d '{"question": "question", "answer": "answer", "category", 1, "difficulty", 1}'  
There is no response JSON.
### POST /search  
Accepts as payload: { 'searchTerm': {search term (case insensitive)}}  
Returns:  
* list of questions in which the question contains the supplied string
* total number of questions  

Sample: curl http://localhost:5000/search -X POST -H "Content-Type: application/json" -d '{"searchTerm": "heaviest"}'
```
{
  "currentCategory": "",
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    }
  ],
  "totalQuestions": 1
}
```

### POST /quiz
Accepts as payload:  
```
    {
        'previous_questions': [{list of id numbers}]
        'quiz_category': { 'type': {category name}, 'id': {category id} }
    }
```
Returns: question in the specified category that was not returned previously in the game  
Sample: curl http://localhost:5000/quiz -X POST -H "Content-Type: application/json" -d '{"previous_questions": [16, 17, 18], "quiz_category": {"type": "Art", "id": 2}}'
{
  "answer": "Jackson Pollock",
  "category": 2,
  "difficulty": 2,
  "id": 19,
  "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
}