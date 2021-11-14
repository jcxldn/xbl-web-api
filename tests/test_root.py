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
