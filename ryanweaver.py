import os
import postgres
from functools import wraps

from flask import Flask, request, render_template, jsonify


app = Flask(__name__)
token = os.environ.get('RYANWEAVER')
db = postgres.Postgres(os.environ.get('DATABASE_URL'))


def _is_in_town():
    return db.one("SELECT traveling FROM status")


def _set_in_town(in_town):
    db.run('UPDATE status SET traveling = %s', (in_town,))


def auth_required(f):
    """
    Accepts either a X-Auth-Token header, or an auth_token parameter.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_token = request.headers.get('X-Auth-Token',
                                         request.args.get('auth_token', None))
        if auth_token != token:
            return jsonify(error='Unauthorized'), 401

        return f(*args, **kwargs)

    return wrapper


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', in_town=_is_in_town())


@app.route('/traveling', methods=['POST', 'PUT'])
@auth_required
def traveling():
    _set_in_town(False)
    return jsonify(in_town=_is_in_town())


@app.route('/in-town', methods=['POST', 'PUT'])
@auth_required
def not_traveling():
    _set_in_town(True)
    return jsonify(in_town=_is_in_town())


if __name__ == '__main__':
    app.run(debug=True)
