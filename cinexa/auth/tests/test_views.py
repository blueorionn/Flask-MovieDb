"""Integration tests — login, logout, profile, protected routes."""

import pytest
from cinexa.conftest import TEST_USERNAME, TEST_PASSWORD


class TestLogin:
    def test_get_returns_form(self, client):
        r = client.get("/auth/login")
        assert r.status_code == 200
        assert b"Sign in to your account" in r.data

    def test_post_valid_redirects(self, client):
        r = client.post(
            "/auth/login",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert r.headers["Location"] == "/"

    def test_post_sets_jwt_cookie(self, client):
        r = client.post(
            "/auth/login",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            follow_redirects=False,
        )
        cookies = r.headers.getlist("Set-Cookie")
        assert any("access_token_cookie" in c for c in cookies)

    def test_post_bad_username(self, client):
        r = client.post(
            "/auth/login", data={"username": "fake", "password": TEST_PASSWORD}
        )
        assert r.status_code == 400
        assert b"Username or password is invalid" in r.data

    def test_post_bad_password(self, client):
        r = client.post(
            "/auth/login", data={"username": TEST_USERNAME, "password": "wrong"}
        )
        assert r.status_code == 400

    def test_post_empty(self, client):
        r = client.post("/auth/login", data={"username": "", "password": ""})
        assert r.status_code == 400


class TestLogout:
    def test_redirects(self, client):
        r = client.get("/auth/logout", follow_redirects=False)
        assert r.status_code == 302

    def test_clears_cookie(self, auth_client):
        r = auth_client.get("/auth/logout", follow_redirects=False)
        assert len(r.headers.getlist("Set-Cookie")) > 0


class TestProfile:
    def test_unauth_returns_401(self, client):
        r = client.get("/auth/user/profile")
        assert r.status_code == 401

    def test_auth_returns_200(self, auth_client):
        r = auth_client.get("/auth/user/profile")
        assert r.status_code == 200
        assert TEST_USERNAME.encode() in r.data


class TestProtectedRoutes:
    @pytest.mark.parametrize(
        "method,url",
        [
            ("GET", "/movies/"),
            ("GET", "/create/"),
            ("POST", "/movie/create/"),
            ("GET", "/movie/update/11111111-1111-1111-1111-111111111111/"),
            ("POST", "/movie/update/11111111-1111-1111-1111-111111111111/"),
        ],
    )
    def test_blocked_for_anonymous(self, client, method, url):
        meth = getattr(client, method.lower())
        r = meth(url)
        assert r.status_code == 401
