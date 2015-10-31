from flask import request
from . import api
from .. import db
#from ..models import Order, Item
from ..models import Message, User, Recipient
from ..decorators import json, paginate


@api.route('/messages/<int:id>/recipients/', methods=['GET'])
@json
@paginate('recipients')
def get_message_recipients(id):
    message = Message.query.get_or_404(id)
    return message.recipients

@api.route('/recipients/<int:id>', methods=['GET'])
@json
def get_recipient(id):
    return Recipient.query.get_or_404(id).export_data()
#
#TODO - route needs to take both a message_id and a user_id!
#@api.route('/messages/<int:id>/recipients/', methods=['POST'])
@api.route('/messages/<int:message_id>/users/<int:user_id>/recipients/', methods=['POST'])
@json
def new_message_recipient(id):
    message = Message.query.get_or_404(message_id)
    user = User.query.get_or_404(user_id)
    recipient = Recipient(message=message, user=user)
    recipient.import_data(request.json)
    db.session.add(recipient)
    db.session.commit()
    return {}, 201, {'Location': recipient.get_url()}

#TODO -- delete?  not sure we need an update method here...
@api.route('/recipients/<int:id>', methods=['PUT'])
@json
def edit_recipient(id):
    recipient = Recipient.query.get_or_404(id)
    recipient.import_data(request.json)
    db.session.add(recipient)
    db.session.commit()
    return {}

@api.route('/recipients/<int:id>', methods=['DELETE'])
@json
def delete_recipient(id):
    recipient = Recipient.query.get_or_404(id)
    db.session.delete(recipient)
    db.session.commit()
    return {}
