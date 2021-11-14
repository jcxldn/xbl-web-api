import pytest

from base import BaseTest


class TestXuid(BaseTest):
    knownData = {"gamertag": "Major Nelson", "xuid": "2584878536129841"}

    firstRequestQueriedAt: str
    firstNonexistentRequestQueriedAt: str

    @pytest.mark.asyncio
    async def test_gamertag(self):
        async with self.session.get("http://localhost:3000/xuid/Major Nelson") as res:
            assert res.status == 200
            assert res.content_type == "application/json"
            assert (await res.json()) == self.knownData
            type(self).firstRequestQueriedAt = res.headers["X-Queried-At"]

    @pytest.mark.asyncio
    async def test_gamertag_repeat(self):
        async with self.session.get("http://localhost:3000/xuid/Major Nelson") as res:
            assert res.status == 200
            assert res.content_type == "application/json"
            assert (await res.json()) == self.knownData
            assert self.firstRequestQueriedAt == res.headers["X-Queried-At"]

    @pytest.mark.asyncio
    async def test_gamertag_raw(self):
        async with self.session.get(
            "http://localhost:3000/xuid/Major Nelson/raw"
        ) as res:
            assert res.status == 200
            assert res.content_type == "text/html"
            assert (await res.text()) == self.knownData["xuid"]
            # Can't check X-Queried-At as it is not carried through

    @pytest.mark.asyncio
    async def test_gamertag_nonexistent(self):
        async with self.session.get(
            "http://localhost:3000/xuid/placeholdergt12"
        ) as res:
            assert res.status == 404
            assert res.content_type == "application/json"
            assert (await res.json()) == {
                "error": "could not resolve gamertag",
                "code": 404,
            }
            type(self).firstNonexistentRequestQueriedAt = res.headers["X-Queried-At"]

    @pytest.mark.asyncio
    async def test_gamertag_nonexistent_repeat(self):
        async with self.session.get(
            "http://localhost:3000/xuid/placeholdergt12"
        ) as res:
            assert res.status == 404
            assert res.content_type == "application/json"
            assert (await res.json()) == {
                "error": "could not resolve gamertag",
                "code": 404,
            }
            assert self.firstNonexistentRequestQueriedAt == res.headers["X-Queried-At"]

    @pytest.mark.asyncio
    async def test_gamertag_nonexistent_raw(self):
        async with self.session.get(
            "http://localhost:3000/xuid/placeholdergt12/raw"
        ) as res:
            # On error, raw passes through the response from the usual endpoint.
            assert res.status == 404
            assert res.content_type == "application/json"
            assert (await res.json()) == {
                "error": "could not resolve gamertag",
                "code": 404,
            }
            # Can't check X-Queried-At as it is not carried through
