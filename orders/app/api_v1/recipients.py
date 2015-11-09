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

#TODO -- AirPair -- need a special route to get all Recipient records for a given friend User....
@api.route('/recipients/<int:friend_id>', methods=['GET'])
@json
@paginate('recipients')
def get_recipients_for_friend(friend_id):
    return Recipient.query.get_or_404(friend_id)

@api.route('/recipients/<int:id>', methods=['GET'])
@json
def get_recipient(id):
    return Recipient.query.get_or_404(id).export_data()

#TODO -- delete?  not sure we need an update method here...
@api.route('/recipients/<int:id>', methods=['PUT'])
@json
def edit_recipient(id):
    recipient = Recipient.query.get_or_404(id)
    recipient.import_data(request.json)
    db.session.add(recipient)
    db.session.commit()
    return {}

'''
don't think this is needed -- can do it through updating the recipients list of a message...
@api.route('/recipients/<int:id>', methods=['DELETE'])
@json
def delete_recipient(id):
    recipient = Recipient.query.get_or_404(id)
    db.session.delete(recipient)
    db.session.commit()
    return {}
'''