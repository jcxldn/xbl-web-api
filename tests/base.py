from aiohttp import ClientSession
import pytest


class BaseTest:
    # Define class variable for making http requests
    session: ClientSession

    # Fixture to get a fresh client session for every test run
    @pytest.fixture(scope="function", autouse=True)
    async def create_session(self):
        # workaround so session is accessible to tests, see: https://github.com/pytest-dev/pytest/issues/3869#issuecomment-488276259
        type(self).session = ClientSession()
        yield
        # Close the session if it isn't already closed
        # eg. test fails so context is not released
        await self.session.close()
