"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Tests user models."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.session.rollback()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
        
    #######################################################################################
    # Testing following and unfollowing
        
    def test_follow(self):
        """ Does following work? """
        
        followed_user = User(
            email = "tester1@testcase.com",
            username = "followed_testuser",
            password = "HASHED_PASSWORD"
        )
        
        following_user = User(
            email = "tester2@testcase.com",
            username = "following_testuser",
            password = "ANOTHER_HASHED_PASSWORD"
        )
        
        db.session.add_all([followed_user, following_user])
        followed_user.followers.append(following_user)
        
        db.session.commit()
        
        self.assertTrue(followed_user.is_followed_by(following_user))
        self.assertTrue(following_user.is_following(followed_user))
        

    def test_unfollow(self):
        """ Deos unfollowing work? """
        
        followed_user = User(
            email = "tester1@testcase.com",
            username = "followed_testuser",
            password = "HASHED_PASSWORD"
        )
        
        following_user_1 = User(
            email = "tester2@testcase.com",
            username = "following_testuser",
            password = "ANOTHER_HASHED_PASSWORD"
        )
        
        following_user_2 = User(
            email = "tester3@testcase.com",
            username = "following_testuser_too",
            password = "ONE_MORE_PASSWORD"
        )
        
        db.session.add_all([followed_user, following_user_1, following_user_2])
        followed_user.followers.append(following_user_1)
        followed_user.followers.append(following_user_2)
        
        db.session.commit()
        
        followed_user.followers.remove(following_user_1)
        
        self.assertEqual(len(followed_user.followers), 1)
        
        
    #######################################################################################
    # Test creating invalid users
        
    def test_create_null_user(self):
        """ Tests that attempting to create a null user behaves as expected """        
        
        with self.assertRaises(Exception):
            
            invalid_user_1 = User(
                email = None,
                username = None,
                password = None
            )
            
            db.session.add(invalid_user_1)
            db.session.commit()
            
            
            
    def test_create_dupe_user(self):
        """ Tests that an error is raised when a user is duped """
        
        with self.assertRaises(Exception):
            valid_user = User(
                email = "test@domain.com",
                username = "same",
                password = "PASSWORD"
            )
            
            db.session.add(valid_user)
            db.session.commit()
            
            duplicated_user = User(
                email = "test@domain.com",
                username = "same",
                password = "PASSWORD"
            )
            
            db.session.add(duplicated_user)
            db.session.commit()
            
            
    #######################################################################################
    # Test user authentication
    
    def test_successful_authentication(self):
        """ Does user.authenticate return a user when given valid credentials? """
        
        username = "testuser"
        password = "HASHED_PASSWORD"
        email = "test@domain.com"
        image_url = "https://randomuser.me/api/portraits/men/83.jpg"
        
        user = User.signup(username=username, email=email, password=password, image_url=image_url)
        self.assertEqual(user.authenticate(username, password), user)
        
        
    def test_invalid_username_authentication(self):
        """ Does user.authenticate return False when given an invaliid username? """
        
        correct_username = "correct"
        incorrect_username = "incorrect"
        password = "HASHED_PASSWORD"
        email = "test@domain.com"
        image_url = "https://randomuser.me/api/portraits/men/83.jpg"
        
        user = User.signup(username=correct_username, email=email, password=password, image_url=image_url)
        
        self.assertFalse(user.authenticate(incorrect_username, password))
        