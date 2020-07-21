import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.drop_all()
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        self.assertEqual(200, res.status_code)
        categories = json.loads(res.data)["categories"]
        self.assertEqual(6, len(categories))

    def test_get_questions_page_1(self):
        res = self.client().get("/questions")
        self.assertEqual(200, res.status_code)
        json_res = json.loads(res.data)
        total_questions = json_res["total_questions"]
        self.assertEqual(10, len(json_res["questions"]))
        self.assertEqual(18, total_questions)

    def test_get_questions_page_2(self):
        res = self.client().get("/questions?page=2")
        self.assertEqual(200, res.status_code)
        json_res = json.loads(res.data)
        total_questions = json_res["total_questions"]
        self.assertEqual(8, len(json_res["questions"]))
        self.assertEqual(18, total_questions)

    def test_get_questions_page_not_found(self):
        res = self.client().get("/questions?page=999")
        self.assertEqual(404, res.status_code)

    def test_get_question_for_categories(self):
        res = self.client().get("/categories/6/questions")
        self.assertEqual(200, res.status_code)
        json_res = json.loads(res.data)
        total_questions = json_res["total_questions"]
        self.assertEqual(2, total_questions)

    def test_delete_question(self):
        res = self.client().delete("/questions/5")
        self.assertEqual(200, res.status_code)
        json_res = json.loads(res.data)
        total_questions = json_res["total_questions"]
        self.assertEqual(18, total_questions)

        res = self.client().post("/questions/search", json={"searchTerm": "caged bird"})
        self.assertEqual(200, res.status_code)
        data = json.loads(res.data)
        total_questions = data["total_questions"]
        questions = data["questions"]
        self.assertEqual(0, total_questions)
        self.assertEqual(0, len(questions))

    def test_post_question(self):
        res = self.client().post(
            "/questions",
            json={
                "question": "test_question",
                "answer": "test_answer",
                "category": "6",
                "difficulty": 3,
            },
        )
        self.assertEqual(200, res.status_code)
        json_res = json.loads(res.data)
        total_questions = json_res["total_questions"]
        self.assertEqual(19, total_questions)

    def test_search_questions(self):
        res = self.client().post("/questions/search", json={"searchTerm": "title"})
        self.assertEqual(200, res.status_code)
        data = json.loads(res.data)
        total_questions = data["total_questions"]
        questions = data["questions"]
        self.assertEqual(1, total_questions)
        self.assertEqual(1, len(questions))

    def test_search_question_empty(self):
        res = self.client().post("/questions/search", json={"searchTerm": ""})
        self.assertEqual(200, res.status_code)
        data = json.loads(res.data)
        total_questions = data["total_questions"]
        questions = data["questions"]
        self.assertEqual(19, total_questions)
        self.assertEqual(19, len(questions))

    def test_get_next_question(self):
        q_id = -1
        previous_questions = []
        res = self.client().post(
            "/next-question",
            json={
                "previous_questions": previous_questions,
                "quiz_category": {"type": "Sports", "id": 6},
            },
        )
        self.assertEqual(200, res.status_code)
        data = json.loads(res.data)
        new_question = data["question"]
        self.assertTrue(new_question["id"] > q_id)
        q_id = new_question["id"]
        self.assertEqual(6, new_question["category"])
        self.assertEqual(1, data["questions_left"])
        previous_questions.append(q_id)

        res = self.client().post(
            "/next-question",
            json={
                "previous_questions": previous_questions,
                "quiz_category": {"type": "Sports", "id": 6},
            },
        )
        self.assertEqual(200, res.status_code)
        data = json.loads(res.data)
        new_question = data["question"]
        self.assertTrue(new_question["id"] is not q_id)
        q_id = new_question["id"]
        self.assertEqual(6, new_question["category"])
        self.assertEqual(0, data["questions_left"])
        previous_questions.append(q_id)

        res = self.client().post(
            "/next-question",
            json={
                "previous_questions": previous_questions,
                "quiz_category": {"type": "Sports", "id": 6},
            },
        )
        self.assertEqual(200, res.status_code)
        data = json.loads(res.data)
        self.assertIsNone(data.get("question"))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
