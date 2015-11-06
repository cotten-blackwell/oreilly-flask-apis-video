#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Message, Recipient

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
    with app.app_context():
        db.create_all()
        # create a development user and some sample data
        if False and User.query.get(1) is None:
            john = User(username='john')
            john.set_password('cat')
            db.session.add(john)
            
            alice = User(username="alice")
            alice.set_password('dog')
            db.session.add(alice)
            db.session.commit()

            cotten = User(username="cotten")
            cotten.set_password('cotten')
            db.session.add(cotten)
            db.session.commit()
            
            victoria = User(username="victoria")
            victoria.set_password('victoria')
            db.session.add(victoria)
            db.session.commit()
            
            message1 = Message(sender_id=john.id)
            db.session.add(message1)
            db.session.commit()

            recipient1 = Recipient(friend_id=alice.id, message_id=message1.id)
            db.session.add(recipient1)
            db.session.commit()

            recipient2 = Recipient(friend_id=cotten.id, message_id=message1.id)
            db.session.add(recipient2)
            db.session.commit()
            
            recipient3 = Recipient(friend_id=victoria.id, message_id=message1.id)
            db.session.add(recipient3)
            db.session.commit()

            message2 = Message(sender_id=john.id)
            db.session.add(message2)
            db.session.commit()
            
            recipient4 = Recipient(friend_id=alice.id, message_id=message2.id)
            db.session.add(recipient4)
            db.session.commit()
            
            recipient5 = Recipient(friend_id=victoria.id, message_id=message2.id)
            db.session.add(recipient5)
            db.session.commit()

    app.run()
