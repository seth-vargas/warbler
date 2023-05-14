"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Tests message models."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.session.rollback()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
        
    def test_messsage_model(self):
        """ Does basic model work? """
        
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        db.session.add(u)
        db.session.commit()

        m = Message(
            text = "This is a test",
            user_id = u.id
        )
        
        db.session.add(m)
        db.session.commit()
        
        self.assertEqual(len(u.messages), 1)
        
        
    def test_liking_message(self):
        """ Does liking a message work as expected? """
        
        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        u2 = User(
            email="tes2t@test.com",
            username="testuser2",
            password="HASHED_PASSWORD_2"
        )
        
        db.session.add_all([u1, u2])
        db.session.commit()

        m = Message(
            text = "This is a test",
            user_id = u1.id
        )
        
        
        db.session.add(m)
        u2.likes.append(m)
        db.session.commit()
        
        self.assertIn(m, u2.likes)
        self.assertEqual(len(u2.likes), 1)
        
        
    def test_deleting_message(self):
        """ 
        Deleting a message should:
        - remove it from Message.query.all()
        - remove it from <user>.likes
        - remove it from <user>.messages
        """
        
        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        u2 = User(
            email="tes2t@test.com",
            username="testuser2",
            password="HASHED_PASSWORD_2"
        )
        
        db.session.add_all([u1, u2])
        db.session.commit()

        m = Message(
            text = "This is a test",
            user_id = u1.id
        )
        
        db.session.add(m)
        db.session.commit()
        
        u2.likes.append(m)
        db.session.commit()
        
        db.session.delete(m)
        db.session.commit()
        
        self.assertEqual(len(Message.query.all()), 0)
        self.assertEqual(len(u2.likes), 0)
        self.assertEqual(len(u1.messages), 0)