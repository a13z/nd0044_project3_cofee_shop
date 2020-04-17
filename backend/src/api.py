import os, sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)

CORS(app, resources={ r'/*': {'origins': '*'}}, supports_credentials=True)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)

    drinks_list = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": drinks_list
    })

'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def get_drink_detail():
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)

    drinks_list = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": drinks_list
    })

'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    body = request.get_json()
    title = body['title']
    recipe = body.get('recipe', [])

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception as e:
        error = true
        print(sys.exc_info())
        print(e)
        abort(422)

'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe', [])

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    
    if drink is None:
        abort(404)
    
    try:
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })

    except Exception as e:
        error = true
        print(sys.exc_info())
        print(e)
        abort(422)

'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    
    if drink is None:
        abort(404)
    
    try:
        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink.id
        })

    except Exception as e:
        error = true
        print(sys.exc_info())
        print(e)
        abort(422)

## Error Handling

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resouce not found"
        }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
        }), 422 

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500   


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(AuthError):
    response = {
        "success": True,
        "error": AuthError.status_code,
        "message": AuthError.error
    }
    return jsonify(response), AuthError.status_code

