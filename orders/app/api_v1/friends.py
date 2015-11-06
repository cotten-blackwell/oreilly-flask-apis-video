from flask import request
from . import api
from .. import db
from ..models import User, Friend
from ..decorators import json, paginate


@api.route('/users/<int:id>/friends/', methods=['GET'])
@json
@paginate('friends')
def get_user_friends(id):
    user = User.query.get_or_404(id)
    return user.friends

@api.route('/friends/<int:id>', methods=['GET'])
@json
def get_friend(id):
    return Friend.query.get_or_404(id).export_data()

#TODO - route needs to take both a to_user_id and a from_user_id!
@api.route('/users/<int:id>/friends/', methods=['POST'])
@json
#def new_user_message(id):
#    #    user = User.query.get_or_404(id)
#    #    message = Message(sender=user)
#    #    message.import_data(request.json)
#    #    db.session.add(message)
#    user = User.query.get_or_404(id)
#    message = Message(sender_id=id)
#    message.import_data(request.json)
#    db.session.add(message)
#    db.session.commit()
#    for recipient in request.json['recipient_ids']:
#        db.session.add(Recipient(friend_id=recipient, message_id=message.id))
#    db.session.commit()
#    return {}, 201, {'Location': message.get_url()}
def new_user_friend(id):
    from_user = User.query.get_or_404(id)
    friend = Friend(from_user_id=id)
    friend.import_data(request.json)
    db.session.add(friend)
    db.session.commit()
    return {}, 201, {'Location': friend.get_url()}
#def new_user_friend(id):
#    from_user = User.query.get_or_404(from_user_id)
#    to_user = User.query.get_or_404(to_user_id)
#    friend = Friend(from_user=from_user, to_user)
#    #TODO -- not sure if we can just delete the next line as not necessary?
#    friend.import_data(request.json)
#    db.session.add(friend)
#    db.session.commit()
#    return {}, 201, {'Location': friend.get_url()}

#TODO -- delete?  not sure we need an update method here...
@api.route('/friends/<int:id>', methods=['PUT'])
@json
def edit_friend(id):
    friend = Friend.query.get_or_404(id)
    friend.import_data(request.json)
    db.session.add(friend)
    db.session.commit()
    return {}

@api.route('/friends/<int:id>', methods=['DELETE'])
@json
def delete_friend(id):
    friend = Friend.query.get_or_404(id)
    db.session.delete(friend)
    db.session.commit()
    return {}
