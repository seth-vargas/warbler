""" User View tests """
# FLASK_ENV=production python -m unittest test_message_views.py

from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from models import db, connect_db, Message, User
from app import app

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


app.config["WTF_CSRF_ENABLED"] = False

db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """ Test views for users. """

    def setUp(self):
        """ Create test client """

        db.session.rollback()

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_list_users(self):
        """ Does the request respond with a list of users? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users")
            container = resp.get_data(as_text=True)
            member = f"<p>@{self.testuser.username}</p>"

            self.assertEqual(resp.status_code, 200)
            self.assertIn(member, container)

    def test_users_show(self):
        """ Does showing a specific user work? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}")
            container = resp.get_data(as_text=True)
            member = f'<h4 id="sidebar-username">@{self.testuser.username}</h4>'

            self.assertEqual(resp.status_code, 200)
            self.assertIn(member, container)

    def test_show_following(self):
        """ Does the request respond with a list of people that testuser is following?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            followed_user = User.signup(username="testuser2",
                                        email="test2@test.com",
                                        password="testuser",
                                        image_url=None)

            # testuser.following = [user]
            followed_user.followers.append(self.testuser)

            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/following")
            container = resp.get_data(as_text=True)
            member = f'<p>@{followed_user.username}</p>'

            self.assertIn(member, container)
            self.assertEqual(resp.status_code, 200)

    def test_users_followers(self):
        """ Does the request respond with a list of people that follow testuser? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            followed_user = User.signup(username="testuser2",
                                        email="test2@test.com",
                                        password="testuser",
                                        image_url=None)

            # testuser.following = [user]
            followed_user.followers.append(self.testuser)

            db.session.commit()

            resp = c.get(f"/users/{followed_user.id}/followers")
            container = resp.get_data(as_text=True)
            member = f'<p>@{self.testuser.username}</p>'

            self.assertIn(member, container)
            self.assertEqual(resp.status_code, 200)

    def test_add_follow(self):
        """ Does this route allow the logged in user to follow someone? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            followed_user = User.signup(username="testuser2",
                                        email="test2@test.com",
                                        password="testuser",
                                        image_url=None)

            db.session.commit()

            resp = c.post(f"/users/follow/{followed_user.id}")

            testuser = User.query.get(self.testuser.id)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(
                resp.location, f"http://localhost/users/{testuser.id}/following")
            self.assertEqual(len(testuser.following), 1)

    def test_stop_following(self):
        """ Does this route allow logged in user to un-follow someone? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            followed_user = User.signup(username="testuser2",
                                        email="test2@test.com",
                                        password="testuser",
                                        image_url=None)

            db.session.commit()

            c.post(f"/users/follow/{followed_user.id}")

            resp = c.post(f"/users/stop-following/{followed_user.id}")

            testuser = User.query.get(self.testuser.id)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(
                resp.location, f"http://localhost/users/{testuser.id}/following")
            self.assertEqual(len(testuser.following), 0)

    def test_show_likes(self):
        """ Should show a list of logged in users liked messages """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/likes")
            container = resp.get_data(as_text=True)
            member = "<h3>Sorry, no liked messages found</h3>"

            self.assertEqual(resp.status_code, 200)
            self.assertIn(member, container)

    def test_add_like(self):
        """ Can a user like some post? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        dummy_user = User.signup(
            username="DUMMY",
            email="DUMMY@test.com",
            password="PASSWORD",
            image_url=None)

        db.session.commit()

        msg = Message(text="TEST", user_id=dummy_user.id)

        db.session.add(msg)
        db.session.commit()

        resp = c.post(f"/users/add_like/{msg.id}")

        testuser = User.query.get(self.testuser.id)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.location, f"http://localhost/users/{self.testuser.id}/likes")
        self.assertEqual(len(testuser.likes), 1)

    def test_GET_profile(self):
        """ Does this GET route show a form? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users/profile")
            container = resp.get_data(as_text=True)
            member = '<h2 class="join-message">Edit Your Profile.</h2>'

            self.assertEqual(resp.status_code, 200)
            self.assertIn(member, container)

    def test_POST_profile(self):
        """ Does this POST route update a user? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/users/profile", data={
                "username": "newusername",
                "password": "testuser"
            })

            testuser = User.query.get(self.testuser.id)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(
                resp.location, f"http://localhost/users/{testuser.id}")
            self.assertEqual(testuser.username, "newusername")

    def test_delete_user(self):
        """ Does the user get deleted? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/users/delete")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(User.query.all()), 0)
