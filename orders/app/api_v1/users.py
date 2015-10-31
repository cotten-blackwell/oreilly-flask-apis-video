from flask import request
from . import api
from .. import db
from ..models import User
from ..decorators import json, paginate


@api.route('/users/', methods=['GET'])
@json
@paginate('users')
def get_users():
    return User.query

@api.route('/users/<int:id>', methods=['GET'])
@json
def get_user(id):
    return User.query.get_or_404(id)

@api.route('/users/', methods=['POST'])
@json
def new_user():
    user = User()
    user.import_data(request.json)
    db.session.add(user)
    db.session.commit()
    return {}, 201, {'Location': user.get_url()}

@api.route('/users/<int:id>', methods=['PUT'])
@json
def edit_user(id):
    user = User.query.get_or_404(id)
    user.import_data(request.json)
    db.session.add(user)
    db.session.commit()
    return {}, 201, {'Location': user.get_url()}
