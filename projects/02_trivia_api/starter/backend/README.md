# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 


## API

[GET] `/categories` 

Fetches  a list of categories, each category has an `id` and a `type` property
- *Example response:*  

```
{
  "categories": [
    {
      "id": 1, 
      "type": "Science"
    }, 
    {
      "id": 2, 
      "type": "Art"
    }
  ], 
  "success": true, 
  "total_categories": 6
}
```

[GET] `/questions` 

Fetches  a list of questions paged with 10 items for each page. It also returns all available categories and 
the total amount of question available in the trivia app.
- *Query parameters:* `page` (by default is set to 1 `/questions?page=1`) asking for an unavailable page should return 404
- *Example response:*  

```
{
  "categories": [
    {
      "id": 5, 
      "type": "Entertainment"
    }, 
  ], 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 5, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }, 
  ], 
  "success": true, 
  "total_questions": 20
}

``` 

[DELETE] `/questions/<q_id>` 

Deletes a question by id, return a json with delete question id and the list of remaining questions and their total number
- *Example response:*  

```
{
  "deleted": "27", 
  "questions": [
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "Scarab", 
      "category": 4, 
      "difficulty": 4, 
      "id": 23, 
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }, 
    {
      "answer": "1994", 
      "category": 5, 
      "difficulty": 3, 
      "id": 25, 
      "question": "Jurassic park is out on theatres"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
``` 

[POST] `/questions`

Creates a new question
- *Body payload*: a json containing a question, an answer, the category and difficulty. For example:
```
{"question":"Question","answer":"Answer","difficulty":1,"category":1}
```
- *Example response:*  

```
{
  "success": true, 
  "total_questions": 21
}
``` 

[POST] `/questions/search`

Searches for a question, the search is case insensitive and is performend with the `ILIKE` operation on the DB
- *Body payload*: a json containing a `searchTerm` containing the searched string
```
{"search": "ameriCa"}
```
- *Example response:*  

```
{
  "questions": [
    {
      "answer": "Jackson Pollock", 
      "category": 2, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ], 
  "success": true, 
  "total_questions": 1
}
``` 

[POST] `/next-question`

Randomly get a question within a specific category, can be called again by sending the previously returned question, in
this case this end point will return a random question selected from the category, but excluding previous questions.
- *Example response:* same as GET `/questions`

[POST] `/questions/search`

Searches for a question, the search is case insensitive and is performend with the `ILIKE` operation on the DB
- *Body payload*: when calling the endpoint for the first time this is how the payload would look like,

```{"previous_questions":[],"quiz_category":{"type":"Geography","id":3}}```

subsequent calls will a have previous questions ids also

```{"previous_questions":[14],"quiz_category":{"type":"Geography","id":3}}```

- *Example response:*  (the answer to the question)

```
{
  "question": {
    "answer": "Agra", 
    "category": 3, 
    "difficulty": 2, 
    "id": 15, 
    "question": "The Taj Mahal is located in which Indian city?"
  }, 
  "questions_left": 1, 
  "success": true
}
```


 