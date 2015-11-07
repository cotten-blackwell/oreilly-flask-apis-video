from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for, current_app
from . import db
from .exceptions import ValidationError
from .utils import split_url

#users_friends = Table(
#    'users_friends', Base.metadata,
#    Column('from_user_id', ForeignKey('users.id'), primary_key=True),
#    Column('to_user_id', ForeignKey('users.id'), primary_key=True),
#)
#

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(256))
    password_hash = db.Column(db.String(128))
#    followers = relationship(
#                             'User',
#                             secondary=users_followers,
#                             primaryjoin=id == users_followers.c.leader_id,
#                             secondaryjoin=id == users_followers.c.follower_id,
#                             backref="leaders",
#                             cascade='all',
#                             )
#    friends = db.relationship('Friend')
    friends = db.relationship(
        'User',
        secondary=Friend,
        primaryjoin=id == friends.c.from_user_id,
        secondaryjoin=id == friends.c.to_user_id,
        backref="from_friends",
        cascade='all',
        )
    sent = db.relationship('Message')
    inbox = db.relationship('Recipient')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def get_url(self):
        return url_for('api.get_user', id=self.id, _external=True)
    
    def export_data(self):
        return {
            'self_url': self.get_url(),
            'username': self.username,
            'email' : self.email,
            'friends' : [f.export_data() for f in self.friends],
            'sent' : [m.export_data() for m in self.sent],
            'inbox': [m.export_data() for m in self.inbox]
        }

    def import_data(self, data):
        try:
            self.username = data['username']
            self.email = data['email']
            self.password_hash = generate_password_hash(data['password'])
        except KeyError as e:
            raise ValidationError('Invalid user: missing ' + e.args[0])
        return self

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    def get_url(self):
        return url_for('api.get_customer', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name,
            'orders_url': url_for('api.get_customer_orders', id=self.id,
                                  _external=True)
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid customer: missing ' + e.args[0])
        return self


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    items = db.relationship('Item', backref='product', lazy='dynamic')

    def get_url(self):
        return url_for('api.get_product', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid product: missing ' + e.args[0])
        return self


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            index=True)
    date = db.Column(db.DateTime, default=datetime.now)
    items = db.relationship('Item', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan')

    def get_url(self):
        return url_for('api.get_order', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'customer_url': self.customer.get_url(),
            'date': self.date.isoformat() + 'Z',
            'items_url': url_for('api.get_order_items', id=self.id,
                                 _external=True)
        }

    def import_data(self, data):
        try:
            self.date = datetime_parser.parse(data['date']).astimezone(
                tzutc()).replace(tzinfo=None)
        except KeyError as e:
            raise ValidationError('Invalid order: missing ' + e.args[0])
        return self


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    date = db.Column(db.DateTime, default=datetime.now)
#    recipients = db.relationship('User', backref='inbox', lazy='subquery', cascade='all')
    file_path = db.Column(db.String(256))
    file_type = db.Column(db.String(64))
    
    def get_url(self):
        return url_for('api.get_message', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'sender_url': url_for('api.get_user', id=self.sender_id),
            'date': self.date.isoformat() + 'Z',
            'file_path': self.file_path,
            'file_type': self.file_type
#            'recipients_url': url_for('api.get_message_recipients', id=self.id,_external=True)
        }

    def import_data(self, data):
        try:
            if data.get('sender_id', None) is not None:
                self.sender_id = data.get('sender_id')
            if data.get('date', None) is not None:
                self.date = datetime_parser.parse(data['date']).astimezone(tzutc()).replace(tzinfo=None)
            #TODO -- how does self.recipients get set?
            #self.recipients = ??
            self.file_path = data['file_path']
            self.file_type = data['file_type']
        except KeyError as e:
            raise ValidationError('Invalid message: missing ' + e.args[0])
        return self
#    def import_data(self, data):
#        try:
#            self.sender_id = int(data['sender_id'])
#            self.date = datetime_parser.parse(data['date']).astimezone(tzutc()).replace(tzinfo=None)
#            #TODO -- how does self.recipients get set?
#            #self.recipients = ??
#            self.file_path = data['file_path']
#            self.file_type = data['file_type']
#        except KeyError as e:
#            raise ValidationError('Invalid message: missing ' + e.args[0])
#        return self


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           index=True)
    quantity = db.Column(db.Integer)

    def get_url(self):
        return url_for('api.get_item', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'order_url': self.order.get_url(),
            'product_url': self.product.get_url(),
            'quantity': self.quantity
        }

    def import_data(self, data):
        try:
            endpoint, args = split_url(data['product_url'])
            self.quantity = int(data['quantity'])
        except KeyError as e:
            raise ValidationError('Invalid order: missing ' + e.args[0])
        if endpoint != 'api.get_product' or not 'id' in args:
            raise ValidationError('Invalid product URL: ' +
                                  data['product_url'])
        self.product = Product.query.get(args['id'])
        if self.product is None:
            raise ValidationError('Invalid product URL: ' +
                                  data['product_url'])
        return self

#TODO -- AirPair question -- Recipient is really more like XrefMessageUser?...
class Recipient(db.Model):
    __tablename__ = 'recipients'
    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), index=True)
        
    def get_url(self):
        return url_for('api.get_recipient', id=self.id, _external=True)

    def export_data(self):
        message = Message.query.get(self.message_id)
        return {
            'self_url': self.get_url(),
            'friend_url': url_for('api.get_user', id=self.friend_id),
            'message': message.export_data()
    }

    def import_data(self, data):
        try:
            #TODO -- AirPair question -- how do friend_id, message_id get set?
            #self.quantity = int(data['quantity'])
            print('for giggles')
        except KeyError as e:
            raise ValidationError('Invalid message: missing ' + e.args[0])
        return self

#TODO -- AirPair question -- Friend is really more like XrefUserUser?...
class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
#    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    def get_url(self):
        return url_for('api.get_friend', id=self.id, _external=True)
    
#    def export_data(self):
#        return {
#            'self_url': self.get_url(),
#            'sender_url': url_for('api.get_user', id=self.sender_id),
#            'date': self.date.isoformat() + 'Z',
#            'file_path': self.file_path,
#            'file_type': self.file_type
#        #            'recipients_url': url_for('api.get_message_recipients', id=self.id,_external=True)
#    }
    def export_data(self):
        return {
            'self_url': self.get_url(),
#            'from_user_url': self.from_user.get_url(),
#            'to_user_url': self.to_user.get_url(),
            'from_user_url': url_for('api.get_user', id=self.from_user_id),
            'to_user_url': url_for('api.get_user', id=self.to_user_id)
        }

#    def import_data(self, data):
#        try:
#            if data.get('sender_id', None) is not None:
#                self.sender_id = data.get('sender_id')
#                if data.get('date', None) is not None:
#                    self.date = datetime_parser.parse(data['date']).astimezone(tzutc()).replace(tzinfo=None)
#            #TODO -- how does self.recipients get set?
#            #self.recipients = ??
#            self.file_path = data['file_path']
#                self.file_type = data['file_type']
#            except KeyError as e:
#                raise ValidationError('Invalid message: missing ' + e.args[0])
#    return self
    def import_data(self, data):
        try:
#            if data.get('from_user_id', None) is not None:
#                self.from_user_id = data.get('from_user_id')
            if data.get('to_user_id', None) is not None:
                self.to_user_id = data.get('to_user_id')
            print('for giggles')
        except KeyError as e:
            raise ValidationError('Invalid relationship: missing ' + e.args[0])
        return self

