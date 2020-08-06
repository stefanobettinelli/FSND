import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES


@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({"success": True, "drinks": [drink.short() for drink in drinks]})


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drink_detail(jwt):
    drinks = Drink.query.all()
    return jsonify({"success": True, "drinks": [drink.long() for drink in drinks]})


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink(jwt):
    body = request.get_json()

    if "title" not in body or "recipe" not in body:
        abort(422)

    title = body.get("title")
    recipe = body.get("recipe")

    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()

    return jsonify({"success": True, "drinks": [drink.long()],})


@app.route("/drinks/<drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    body = request.get_json()

    title = body.get("title")
    recipe = body.get("recipe")

    if "title" not in body and "recipe" not in body:
        abort(422)

    drink.title = title
    drink.title = recipe
    drink.update()

    return jsonify({"success": True, "drinks": [drink.long()]})


@app.route("/drinks/<drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete(jwt, drink_id):
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    drink.delete()

    return jsonify({"success": True, "delete": drink_id})


"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return (
        jsonify({"success": False, "error": ex.status_code, "message": ex.error}),
        401,
    )
