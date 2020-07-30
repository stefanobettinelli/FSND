import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import randint
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def get_pages_n(data_len):
    return (
        data_len // QUESTIONS_PER_PAGE
        if data_len % QUESTIONS_PER_PAGE is 0
        else data_len // QUESTIONS_PER_PAGE + 1
    )


def get_formatted_categories(categories):
    formatted_categories = {}
    for category in categories:
        formatted_categories[category.id] = category.type
    return formatted_categories


def get_page(data, page, page_size):
    if data is None:
        return []
    pages_number = get_pages_n(len(data))
    if page not in range(1, pages_number + 1):
        abort(404)
    start = (page - 1) * page_size
    end = start + page_size
    return data[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    @app.route("/categories")
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = get_formatted_categories(categories)
        return jsonify(
            {
                "success": True,
                "categories": formatted_categories,
                "total_categories": len(categories),
            }
        )

    @app.route("/questions")
    def get_questions():
        all_questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        page = request.args.get("page", 1, type=int)
        questions_page = get_page(all_questions, page, QUESTIONS_PER_PAGE)
        res_questions = [question.format() for question in questions_page]
        formatted_categories = get_formatted_categories(categories)
        return jsonify(
            {
                "success": True,
                "questions": res_questions,
                "categories": formatted_categories,
                "total_questions": len(all_questions),
            }
        )

    @app.route("/questions/<q_id>", methods=["DELETE"])
    def delete_question(q_id):
        question_to_delete = Question.query.get(q_id)
        question_to_delete.delete()
        questions = Question.query.order_by(Question.id).all()
        res = [question.format() for question in questions]
        return jsonify(
            {
                "success": True,
                "deleted": q_id,
                "questions": res,
                "total_questions": len(res),
            }
        )

    @app.route("/questions", methods=["POST"])
    def post_question():
        body = request.get_json()
        question = body.get("question")
        answer = body.get("answer")
        category = body.get("category")
        difficulty = body.get("difficulty")
        question = Question(
            question=question, answer=answer, category=category, difficulty=difficulty
        )
        question.insert()
        questions = Question.query.order_by(Question.id).all()
        res = [question.format() for question in questions]
        return jsonify({"success": True, "total_questions": len(res)})

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        search_term = request.get_json().get("searchTerm")
        if search_term is None:
            abort(400)

        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()
        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in questions],
                "total_questions": len(questions),
            }
        )

    @app.route("/categories/<cat_id>/questions")
    def get_question_for_categories(cat_id):
        questions = (
            Question.query.join(Category, Category.id == Question.category)
            .filter(Question.category == cat_id)
            .order_by(Question.id)
            .all()
        )
        page = request.args.get("page", 1, type=int)
        questions_page = get_page(questions, page, QUESTIONS_PER_PAGE)
        res = [question.format() for question in questions_page]
        return jsonify({"success": True, "questions": res, "total_questions": len(res)})

    @app.route("/quizzes", methods=["POST"])
    def get_next_question():
        quiz_category = request.get_json().get("quiz_category")
        previous_questions_ids = request.get_json().get("previous_questions")

        if quiz_category is None or previous_questions_ids is None:
            abort(400)

        prev_questions_ids = [q_id for q_id in previous_questions_ids]

        cat_questions = None
        if quiz_category["id"] == 0:
            cat_questions = Question.query.all()
        else:
            cat_questions = Question.query.filter(
                Question.category == quiz_category["id"]
            ).all()
        questions = [q for q in cat_questions if q.id not in prev_questions_ids]

        if len(questions) <= 0:
            return jsonify({"success": True, "questions_left": 0})

        rand_index = randint(0, len(questions) - 1)
        return jsonify(
            {
                "success": True,
                "question": questions[rand_index].format(),
                "questions_left": len(questions) - 1,
            }
        )

    @app.errorhandler(400)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 400, "message": "Bad request"}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 500, "message": "Backend error"}),
            500,
        )

    return app
