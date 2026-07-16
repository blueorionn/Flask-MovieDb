"""Unit tests for core.func"""

import copy
import mongomock
from cinexa.core.func import (
    list_movies,
    create_movie,
    update_movie,
    get_movie,
    list_series,
)

SEED_DOCS = [
    {
        "id": "40b5d19b-3513-453f-a2ff-ad47c86b2b57",
        "created_by": "c4d8555e-71c1-440d-b720-662094204a80",
        "is_private": False,
        "title": "The Shawshank Redemption",
        "release_year": 1994,
        "rating": 9.3,
        "genre": ["Drama"],
        "poster": "the-shawshank-redemption.jpg",
        "description": "Chronicles the experiences of a formerly successful banker as a prisoner in the gloomy jailhouse of Shawshank after being found guilty of a crime he did not commit. The film portrays the man's unique way of dealing with his new, torturous life; along the way he befriends a number of fellow prisoners, most notably a wise long-term inmate named Red",
    },
    {
        "id": "9a761fb8-7465-4985-983d-5faceb3735f0",
        "created_by": "c4d8555e-71c1-440d-b720-662094204a80",
        "is_private": False,
        "title": "The Godfather",
        "release_year": 1972,
        "rating": 9.2,
        "genre": ["Crime"],
        "poster": "the-godfather.jpg",
        "description": "The Godfather 'Don' Vito Corleone is the head of the Corleone mafia family in New York. He is at the event of his daughter's wedding. Michael, Vit's youngest son and a decorated WWII Marine is also present at the wedding. Michael seems to be uninterested in being a part of the family business.",
    },
    {
        "id": "7e3dc43a-4978-4d61-9c9b-d77d859b82a7",
        "created_by": "c4d8555e-71c1-440d-b720-662094204a80",
        "is_private": True,
        "title": "The Dark Knight",
        "release_year": 2008,
        "rating": 9.0,
        "genre": ["Crime"],
        "poster": "the-dark-knight.jpg",
        "description": "When a menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman, James Gordon and Harvey Dent must work together to put an end to the madness.",
    },
]

SERIES_DATA = {
    "series": [
        {
            "id": "3812bdb6-32d5-4180-9b09-264867f2d165",
            "author": "c4d8555e-71c1-440d-b720-662094204a80",
            "is_private": False,
            "title": "Over the Garden Wall",
            "release_year": 2014,
            "genre": ["Animation", "Adventure", "Drama", "Horror"],
            "poster": "over-the-garden-wall.jpg",
            "description": "Somewhere, lost in the clouded annals of history, lies a place that few have seen. A mysterious place called The Unknown... Two Brothers, Wirt and Greg find themselves lost in the strange woods, adrift in a time. With the help of a shadowy Woodsmen and a foul-tempered bluebird named Beatrice, they travel through the foggy land in Hope of finding a way home.",
            "seasons": 1,
        }
    ],
    "episodes": [
        {
            "series": "3812bdb6-32d5-4180-9b09-264867f2d165",
            "id": "b51445b0-36ba-436f-9e5f-4dc6dda7c212",
            "serial": {"season": 1, "episode": 1},
            "title": "The Old Grist Mill",
            "description": "Wirt and Gregory meet the Woodsman and learn about the Beast.",
            "rating": 8.4,
            "release_year": 2014,
        },
        {
            "series": "3812bdb6-32d5-4180-9b09-264867f2d165",
            "id": "af1c2f94-d88a-4be4-baf3-5c959ee0de87",
            "serial": {"season": 1, "episode": 2},
            "title": "Hard Times at the Huskin' Bee",
            "description": "The brothers visit a town of pumpkin people and participate in a festival.",
            "rating": 8.2,
            "release_year": 2014,
        },
        {
            "series": "3812bdb6-32d5-4180-9b09-264867f2d165",
            "id": "5881dcdb-6ce9-44ad-bbfa-077cf7379e2e",
            "serial": {"season": 1, "episode": 3},
            "title": "Schooltown Follies",
            "description": "They encounter a school attended by animals and a mysterious teacher.",
            "rating": 8.3,
            "release_year": 2014,
        },
    ],
}


def _seeded_db(include_series=False):
    client = mongomock.MongoClient()
    db = client["testdb"]
    db["movie"].insert_many(copy.deepcopy(SEED_DOCS))

    if include_series:
        db["series"].insert_many(copy.deepcopy(SERIES_DATA["series"]))
        db["episode"].insert_many(copy.deepcopy(SERIES_DATA["episodes"]))

    import cinexa.core.func as mod

    mod.get_db = lambda: db  # Mock get_db to return our seeded db


def _without_id(doc):
    """Return a copy of a MongoDB document without the ``_id`` field."""
    return {k: v for k, v in doc.items() if k != "_id"}


class TestListMovies:
    def test_list_all(self):
        _seeded_db()
        results = list_movies({})
        assert len(results) == 3
        assert [_without_id(r) for r in results] == SEED_DOCS

    def test_list_public_only(self):
        _seeded_db()
        results = list_movies({"is_private": False})
        assert len(results) == 2
        assert _without_id(results[0])["title"] == "The Shawshank Redemption"
        assert _without_id(results[1])["title"] == "The Godfather"

    def test_list_private_only(self):
        _seeded_db()
        results = list_movies({"is_private": True})
        assert len(results) == 1
        assert _without_id(results[0])["title"] == "The Dark Knight"


class TestGetMovie:
    def test_get_existing(self):
        _seeded_db()
        movie = get_movie("40b5d19b-3513-453f-a2ff-ad47c86b2b57")
        assert movie is not None
        assert _without_id(movie) == SEED_DOCS[0]

    def test_get_missing(self):
        _seeded_db()
        assert get_movie("nonexistent-id") is None


class TestCreateMovie:
    def test_create(self):
        _seeded_db()
        result = create_movie(
            id="130c1d1f-7386-4ab1-9319-52f11a424f52",
            user_id="c4d8555e-71c1-440d-b720-662094204a80",
            title="Inception",
            release_year=2010,
            rating=8.8,
            genre=["Sci-Fi", "Action"],
            poster="inception.jpg",
            description="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO.",
            is_private=False,
        )
        assert result is True

        # Verify it was actually inserted
        movie = get_movie("130c1d1f-7386-4ab1-9319-52f11a424f52")
        assert movie is not None
        assert movie["title"] == "Inception"
        assert movie["release_year"] == 2010
        assert movie["rating"] == 8.8


class TestUpdateMovie:
    def test_update(self):
        _seeded_db()
        result = update_movie(
            "40b5d19b-3513-453f-a2ff-ad47c86b2b57",
            {
                "title": "The Shawshank Redemption (Special Edition)",
                "rating": 9.5,
            },
        )
        assert result is True

        # Verify the update was applied
        movie = get_movie("40b5d19b-3513-453f-a2ff-ad47c86b2b57")
        assert movie["title"] == "The Shawshank Redemption (Special Edition)"
        assert movie["rating"] == 9.5
        # Unchanged fields should remain
        assert movie["release_year"] == 1994

    def test_update_nonexistent(self):
        _seeded_db()
        result = update_movie("nonexistent-id", {"title": "Ghost"})
        assert result is True  # Function returns True regardless


class TestListSeries:
    def test_list_all(self):
        _seeded_db(include_series=True)
        results = list_series({})
        assert len(results) == 1
        series = _without_id(results[0])
        assert series["id"] == "3812bdb6-32d5-4180-9b09-264867f2d165"
        assert series["title"] == "Over the Garden Wall"
        assert series["episode_count"] == 3

    def test_list_public_only(self):
        _seeded_db(include_series=True)
        results = list_series({"is_private": False})
        assert len(results) == 1

    def test_list_no_series_seeded(self):
        _seeded_db(include_series=False)
        results = list_series({})
        assert results == []
