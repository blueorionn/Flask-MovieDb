"""Integration tests for core views — movies, series, posters."""

import copy
from unittest.mock import patch

import pytest
from cinexa.conftest import TEST_USER_ID

SEED_MOVIES = [
    {
        "id": "40b5d19b-3513-453f-a2ff-ad47c86b2b57",
        "created_by": TEST_USER_ID,
        "is_private": False,
        "title": "The Shawshank Redemption",
        "release_year": 1994,
        "rating": 9.3,
        "genre": "Drama",
        "poster": "the-shawshank-redemption.jpg",
        "description": "Two imprisoned men bond over a number of years.",
    },
    {
        "id": "9a761fb8-7465-4985-983d-5faceb3735f0",
        "created_by": TEST_USER_ID,
        "is_private": False,
        "title": "The Godfather",
        "release_year": 1972,
        "rating": 9.2,
        "genre": "Crime",
        "poster": "the-godfather.jpg",
        "description": "The aging patriarch of an organized crime dynasty.",
    },
    {
        "id": "7e3dc43a-4978-4d61-9c9b-d77d859b82a7",
        "created_by": "550e8400-e29b-41d4-a716-446655440000",  # different user
        "is_private": True,
        "title": "The Dark Knight",
        "release_year": 2008,
        "rating": 9.0,
        "genre": "Crime",
        "poster": "the-dark-knight.jpg",
        "description": "When the Joker wreaks havoc on Gotham.",
    },
]

SEED_SERIES = [
    {
        "id": "3812bdb6-32d5-4180-9b09-264867f2d165",
        "author": TEST_USER_ID,
        "is_private": False,
        "title": "Over the Garden Wall",
        "release_year": 2014,
        "genre": "Animation",
        "poster": "over-the-garden-wall.jpg",
        "description": "Two brothers lost in a strange wood.",
        "seasons": 1,
    }
]

SEED_EPISODES = [
    {
        "series": "3812bdb6-32d5-4180-9b09-264867f2d165",
        "id": "b51445b0-36ba-436f-9e5f-4dc6dda7c212",
        "serial": {"season": 1, "episode": 1},
        "title": "The Old Grist Mill",
        "rating": 8.4,
        "release_year": 2014,
    },
]


def _seed_movies(app):
    with app.app_context():
        from cinexa.extensions import get_db

        get_db()["movie"].insert_many(copy.deepcopy(SEED_MOVIES))


def _seed_series(app):
    with app.app_context():
        from cinexa.extensions import get_db

        get_db()["series"].insert_many(copy.deepcopy(SEED_SERIES))
        get_db()["episode"].insert_many(copy.deepcopy(SEED_EPISODES))


class TestMoviesView:
    """GET / — display public movies."""

    def test_lists_public_movies(self, client, app):
        _seed_movies(app)
        r = client.get("/")
        assert r.status_code == 200
        assert b"The Shawshank Redemption" in r.data
        assert b"The Godfather" in r.data

    def test_hides_private_movies_from_anonymous(self, client, app):
        _seed_movies(app)
        r = client.get("/")
        assert b"The Dark Knight" not in r.data

    def test_authenticated_sees_own_private_movies(self, auth_client, app):
        _seed_movies(app)
        r = auth_client.get("/")
        assert r.status_code == 200
        assert b"The Shawshank Redemption" in r.data
        # The Dark Knight is owned by a different user, so still hidden
        assert b"The Dark Knight" not in r.data

    def test_empty_index(self, client):
        r = client.get("/")
        assert r.status_code == 200


class TestGetMovie:
    """GET /movie/<id>/ — show a single movie."""

    def test_existing_movie(self, client, app):
        _seed_movies(app)
        r = client.get("/movie/40b5d19b-3513-453f-a2ff-ad47c86b2b57/")
        assert r.status_code == 200
        assert b"The Shawshank Redemption" in r.data

    def test_missing_movie(self, client):
        r = client.get("/movie/00000000-0000-0000-0000-000000000000/")
        assert r.status_code == 404


class TestSeriesView:
    """GET /series/ — list public series."""

    def test_lists_series(self, client, app):
        _seed_series(app)
        r = client.get("/series/")
        assert r.status_code == 200

    def test_empty_series(self, client):
        r = client.get("/series/")
        assert r.status_code == 200


class TestServePoster:
    """GET /movie/poster/<filename> — redirect to S3."""

    def test_redirects_to_s3(self, client):
        r = client.get("/movie/poster/test.jpg", follow_redirects=False)
        assert r.status_code == 302
        assert "posters/test.jpg" in r.headers["Location"]


class TestProtectedRoutes:
    """All routes that require JWT authentication."""

    @pytest.mark.parametrize(
        "method,url",
        [
            ("GET", "/create/"),
            ("GET", "/movies/"),
            ("POST", "/movie/create/"),
            ("GET", "/movie/update/11111111-1111-1111-1111-111111111111/"),
            ("POST", "/movie/update/11111111-1111-1111-1111-111111111111/"),
        ],
    )
    def test_blocked_for_anonymous(self, client, method, url):
        meth = getattr(client, method.lower())
        r = meth(url)
        assert r.status_code == 401

    def test_create_page_for_authenticated(self, auth_client):
        r = auth_client.get("/create/")
        assert r.status_code == 200

    def test_your_movies_for_authenticated(self, auth_client):
        r = auth_client.get("/movies/")
        assert r.status_code == 200
