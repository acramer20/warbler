"""User model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u = User.signup("test1", "email1@email.com", "password", None)
        self.uid = 1111
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="TestText",
            user_id= self.uid
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, 'TestText')

    def test_message_likes(self):
        """Does the basic like function"""
        m1 = Message(
            text="TestText",
            user_id= self.uid
        )
        m2 = Message(
            text="WarblyWarble",
            user_id= self.uid
        )

        db.session.add_all([m1, m2])
        db.session.commit()

        u2 = User.signup("test2", "email2@email.com", "password", None)
        self.uid2 = 2222
        u2.id = self.uid2
        db.session.add(u2)
        db.session.commit()

        u2.likes.append(m1)
        db.session.commit()

        liked_message = Likes.query.filter(Likes.user_id == self.uid2).all()
        self.assertEqual(len(liked_message), 1)
        self.assertEqual(liked_message[0].message_id, m1.id)

