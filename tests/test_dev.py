import pytest

from base import BaseTest

# Not including /dev/reauth as it is due to be removed soon
class TestDev(BaseTest):
    @pytest.mark.asyncio
    async def test_isauth(self):
        async with self.session.get("http://localhost:3000/dev/isauth") as res:
            assert res.status == 200
            assert res.content_type == "application/json"
            # We can use the keyword True here as aiohttp will automatically convert from a JSON boolean when parsing
            assert (await res.json()) == {"authenticated": True}
