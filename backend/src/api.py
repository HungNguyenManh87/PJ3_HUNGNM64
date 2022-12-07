import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import logging
from logging import Formatter, FileHandler

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('./api.log', 'w', 'utf-8')
root_logger.addHandler(handler)

app = Flask(__name__)
setup_db(app)
CORS(app)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

@app.after_request
def after_request(response):
    response.headers.add(
                'Allow-Control-Allow-Headers',
                'Content-Type,Authorization,true'
                )
    response.headers.add(
                'Allow-Control-Allow-Methods',
                'GET, POST, PATCH, DELETE, OPTIONS'
                )

    return response

# ROUTES
with app.app_context():
    @app.route('/drinks', methods=['GET'])
    def get_drinks():
        root_logger.info("===api.py :get drinks===")
        drinks = Drink.query.all()
        
        if len(drinks) == 0:
            root_logger.info("===api.py :Error 404\
                             dont have any drink=== line 51")
            abort(404)

        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200

    @app.route('/drinks-detail', methods=['GET'])
    @requires_auth('get:drinks-detail')
    def get_drinks_details(jwt):
        root_logger.info("===api.py :get drinks detail ===")
        drinks = Drink.query.all()
        if len(drinks) == 0:
            root_logger.info("===api.py :Error 404\
                             dont have any drink===line 65")
            abort(404)

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200

    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def create_drinks(jwt):
        root_logger.info("===api.py :Create drinks ===")
        body = request.get_json()
        if body is None:
            root_logger.info("===api.py :Error 400 \
                             request dont have body===line 79")
            abort(400)

        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if (title is None) or (recipe is None):
            root_logger.info("===api.py :Error 400 \
                            title/recipe is not set\
                            ===line 85") 
            abort(400)

        if not isinstance(recipe, list):
            root_logger.info("===api.py :Error 422 \
                             type of recipe not is the list type\
                              ===line 89") 
            abort(422)

        drink = Drink(title=title, recipe=json.dumps(recipe))
        try:
            drink.insert()
        except Exception as e:
            root_logger.info("===api.py :Error 422 \
                             error when insert Drink \
                              ===line 105")
            root_logger.info(e) 
            abort(422)

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200


    @app.route('/drinks/<int:drink_id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def update_drink(jwt, drink_id):
        root_logger.info("===api.py :Update drinks ===")
        drink = Drink.query.get(drink_id)
        if drink is None:
            root_logger.info("===api.py :Error 404 \
                    can not get Drinkid" + str(drink_id)  + " from database \
                    ===line 122") 
            abort(404)

        body = request.get_json()
        if body is None:
            root_logger.info("===api.py :Error 400 \
            can not get Drink data from request  \
            ===line 128") 
            abort(400)

        title = body.get('title', None)
        recipe = body.get('recipe', None)
        if title:
            drink.title = title
        if recipe:
            try:
                drink.recipe = json.dumps(recipe)
            except Exception as e:
                root_logger.info("===api.py :Error 400 \
                can not get Drink  recipe data from request  \
                ===line 140") 
                abort(400)
        try:
            drink.update()
        except Exception as e:
            root_logger.info("===api.py :Error 422 \
            Error when update drink \
            ===line 148") 
            abort(422)

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(jwt, drink_id):
        root_logger.info("===api.py :Delete drinks ===")
        drink = Drink.query.get(drink_id)
        if drink is None:
            root_logger.info("===api.py :Error 404 \
            can not get Drinkid" + str(drink_id)  + " from database \
            ===line 122") 
            abort(404)
        try:
            drink.delete()
        except Exception as e:
            root_logger.info("===api.py :Error 422 \
            Error when delete drink \
            ===line 148") 
            abort(422)

        return jsonify({
            'success': True,
            'delete': drink.id
        }), 200

    # Error Handling

    # Error 422
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    # Error 400
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    # Error 401
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 401,
            'message': 'Unauthorized'
        }), 401

    # Error 403
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 403,
            'message': 'Permission not allowed'
        }), 403

    # Error 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    # Error 405
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    # Error 422
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    # Error 500
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Server error'
        }), 500
