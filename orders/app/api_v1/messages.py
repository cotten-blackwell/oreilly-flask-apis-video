from flask import request
from . import api
from .. import db
#from ..models import Order, Customer
from ..models import Message, User
from ..decorators import json, paginate


@api.route('/messages/', methods=['GET'])
@json
@paginate('messages')
def get_messages():
    return Message.query

@api.route('/users/<int:id>/messages/', methods=['GET'])
@json
@paginate('messages')
def get_user_messages(id):
    user = User.query.get_or_404(id)
    return user.messages

@api.route('/messages/<int:id>', methods=['GET'])
@json
def get_message(id):
    return Message.query.get_or_404(id)

@api.route('/users/<int:id>/messages/', methods=['POST'])
@json
def new_user_message(id):
    user = User.query.get_or_404(id)
    message = Message(sender=user)
    message.import_data(request.json)
    db.session.add(message)
    db.session.commit()
    return {}, 201, {'Location': message.get_url()}

@api.route('/messages/<int:id>', methods=['PUT'])
@json
def edit_message(id):
    message = Message.query.get_or_404(id)
    order.import_data(request.json)
    db.session.add(message)
    db.session.commit()
    return {}

@api.route('/messages/<int:id>', methods=['DELETE'])
@json
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return {}
    