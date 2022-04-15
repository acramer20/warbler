"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser2_id = 2345
        self.testuser2.id = self.testuser2_id

        self.testuser3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser3",
                                    image_url=None)
        self.testuser3_id = 3456
        self.testuser3.id = self.testuser3_id

        self.testuser4 = User.signup(username="testuser4",
                                    email="test4@test.com",
                                    password="testuser4",
                                    image_url=None)
        self.testuser3_id = 4567
        self.testuser3.id = self.testuser3_id

        db.session.commit()
    
    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.testuser2_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.testuser3_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.testuser2_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_show_others_followers(self):
        """shows the followers pages of any user"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@testuser2", str(resp.data))
            self.assertNotIn("@testuser3", str(resp.data))
    
    def test_show_others_following(self):
        """shows the following pages of any user"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get(f"/users/{self.testuser_id}/following")

            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@testuser3", str(resp.data))
            self.assertNotIn("@testuser4", str(resp.data))

    def test_unauthenticated_following_page_view(self):
        """not logged in so cannot see other users' following pages"""
        self.setup_followers()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthenticated_followers_page_view(self):
        """not logged in so cannot see other users' followers pages"""
        self.setup_followers()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))