"""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        
        u1 = User.signup("test1", "test1@gmail.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "test2@gmail.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

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

    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u1.following[0].id, self.u2.id)
        self.assertEqual(self.u2.followers[0].id, self.u1.id)

    def test_user_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))
    
    def test_user_is_followed(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    # ***************** Signup Tests ********************

    def test_user_signup(self):
        test_u1 = User.signup("testing123", "testytester@test.com", "password", None)
        uid = 77777
        test_u1.id = uid
        db.session.commit()

        test_u1 = User.query.get(uid)
        self.assertEqual(test_u1.username, "testing123")        
        self.assertEqual(test_u1.email, "testytester@test.com")        
        self.assertNotEqual(test_u1.password, "password")        
        self.assertTrue(test_u1.password.startswith("$2b$"))

    def test_signup_fail_username(self):
        failed = User.signup(None, "testing@test.com", "password", None)
        uid = 99999
        failed.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_fail_email(self):
        failed = User.signup("Testerboi", None, "password", None)
        uid = 12345678
        failed.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_fail_password(self):
        with self.assertRaises(ValueError) as context:
            User.signup("Testing1212", "test@test.com", "", None)

    # ******************* Authentication Testing *******************

    def test_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertEqual(u.id, self.uid1)

    def test_authentication_username_invalid(self):
        self.assertFalse(User.authenticate("invalidusername", "password"))

    def test_authentication_password_invalid(self):
        self.assertFalse(User.authenticate(self.u1.username, "invalidPassword"))


    

    


