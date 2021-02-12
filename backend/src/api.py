import json
from flask import (
    request,
    Flask,
    abort,
    jsonify,
    flash,
    session
)
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from flask_cors import CORS


app = Flask(__name__)
setup_db(app)
CORS(app)
app.secret_key = "super secret key"


# db_drop_and_create_all()


def format_response(format_type, obj):
    if format_type == 'long':
        result = [drink.long() for drink in obj]
    elif format_type == 'short':
        result = [drink.long() for drink in obj]
    else:
        result = None
    return result


def drink_actions(action, id, title, recipe):
    error = False
    if action == 'insert':
        try:
            add_drink = Drink(title=title, recipe=recipe)
            add_drink.insert()
        except:
            error = True
        if error:
            flash(title + ' could not be added due to An error occurred.')
        if not error:
            flash('Drink ' + title + ' successfully Added!')
        return [add_drink.long()]
    elif action == 'update':
        drink_update = Drink.query.filter_by(id=id).first()
        if drink_update:
            try:
                drink_update.title = title
                drink_update.recipe = recipe
                drink_update.update()
            except:
                error = True
            if error:
                flash(title + ' could not be Updated due to An error occurred.')
            if not error:
                flash('Drink ' + title + ' successfully Updated!')
            return [drink_update.long()]
        else:
            abort(404)
    elif action == 'del':
        drink_del = Drink.query.filter_by(id=id).first()
        if drink_del:
            try:
                drink_del.delete()
            except:
                error = True
            if error:
                flash(title + ' could not be Deleted due to An error occurred.')
            if not error:
                flash('Drink ' + title + ' successfully Deleted!')
            return id
        else:
            abort(404)
    else:
        abort(404)


@app.route('/drinks')
def drinks():
    all_drinks = Drink.get(Drink)
    if all_drinks:
        return jsonify({
            'success': True,
            'drinks': format_response('short', all_drinks)
        }), 200
    else:
        abort(404)


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    all_drinks = Drink.get(Drink)
    if all_drinks:
        return jsonify({
            'success': True,
            'drinks': format_response('long', all_drinks)
        }), 200
    else:
        abort(404)


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    data = request.get_json()
    if data is None:
        abort(406)
    if not ('title' in data and 'recipe' in data):
        abort(422)
    else:
        return jsonify({
            'success': True,
            'drinks': drink_actions('insert', 0, data.get('title'), json.dumps(data.get('recipe'))),
        })


@app.route("/drinks/<int:id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    data = request.get_json()
    if data is None:
        abort(406)
    else:
        return jsonify({
            'success': True,
            'drinks': drink_actions('update', id, data.get('title'), json.dumps(data.get('recipe'))),
        })


@app.route("/drinks/<int:id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    return jsonify({
        'success': True,
        'drinks': drink_actions('del', id, '', ''),
    })


# Error Handling
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        'message': ex.error
    }), ex.status_code


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "The browser (or proxy) sent a request that this server could not understand"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Access to the requested resource is forbidden"
    }), 403


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(405)
def invalid_method(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


@app.errorhandler(409)
def duplicate_resource(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "The request could not be completed due to a conflict"
    }), 409


@app.errorhandler(406)
def not_accepted(error):
    return jsonify({
        "success": False,
        "error": 406,
        "message": "Not Accepted Request"
    }), 406


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500
