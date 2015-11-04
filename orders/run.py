#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Message, Recipient

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
    with app.app_context():
        db.create_all()
        # create a development user
        if User.query.get(1) is None:
            u = User(username='john')
            u.set_password('cat')
            db.session.add(u)
            alice = User(username="alice")
            alice.set_password('dog')
            db.session.add(alice)
            db.session.commit()
            m = Message(sender_id=u.id)
            db.session.add(m)
            db.session.commit()
            r = Recipient(friend_id=alice.id, message_id=m.id)
            db.session.add(r)
            db.session.commit()
    app.run()
