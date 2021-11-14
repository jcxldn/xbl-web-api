import subprocess
import pytest

from base import BaseTest


class TestRoot(BaseTest):
    @pytest.mark.asyncio
    async def test_index(self):
        async with self.session.get("http://localhost:3000") as res:
            assert res.status == 200
            assert res.content_type == "text/html"

    @pytest.mark.asyncio
    async def test_readme(self):
        async with self.session.get("http://localhost:3000/readme") as res:
            assert res.status == 200
            assert res.content_type == "text/markdown"
            assert (
                str(await res.text()).replace("\r", "")
                == open("README.md", mode="r").read()
            )

    @pytest.mark.asyncio
    async def test_info(self):
        async with self.session.get("http://localhost:3000/info") as res:
            assert res.status == 200
            assert res.content_type == "application/json"
            # Code copied from server.py when env var not available
            assert (await res.json())["sha"] == str(
                subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
            ).split("'")[1::2][0]

    @pytest.mark.asyncio
    async def test_titleinfo(self):
        # Known attributes for Forza Horizon 2
        knownAttributes = {
            "titleId": "446059611",
            "pfn": "Microsoft.ForzaHorizon2_8wekyb3d8bbwe",
            "scid": "788f0100-a4bc-46c3-b19b-d1001a96545b",
        }
        async with self.session.get(
            "http://localhost:3000/titleinfo/%s" % knownAttributes["titleId"]
        ) as res:
            assert res.status == 200
            data: dict = await res.json()
            # TODO: possible for old XDK (launch Xbox One games) to have classic title / product ids?
            # TODO: Cross-reference data with catalog lookup
            assert data["titles"][0]["titleId"] == knownAttributes["titleId"]
            assert data["titles"][0]["modernTitleId"] == knownAttributes["titleId"]
            assert data["titles"][0]["pfn"] == knownAttributes["pfn"]
            assert data["titles"][0]["serviceConfigId"] == knownAttributes["scid"]

    @pytest.mark.asyncio
    async def test_legacysearch(self):
        async with self.session.get("http://localhost:3000/legacysearch/value") as res:
            assert res.status == 410
            assert (await res.json()) == {
                "error": "legacysearch not currently available",
                "code": 410,
            }

    @pytest.mark.asyncio
    async def test_gamertagcheck_taken(self):
        async with self.session.get(
            "http://localhost:3000/gamertag/check/Major Nelson"
        ) as res:
            assert res.status == 200
            assert (await res.json()) == {"available": "false"}

    @pytest.mark.asyncio
    async def test_gamertagcheck_available(self):
        async with self.session.get(
            "http://localhost:3000/gamertag/check/placeholdergt12"
        ) as res:
            assert res.status == 200
            assert (await res.json()) == {"available": "true"}

    # TODO: Unknown test (currently returns 500?)
    # Likely because of invalid gamertag
