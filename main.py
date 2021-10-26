import sys
import os
import time
import asyncio

import coloredlogs

# Setup logging
coloredlogs.install(level='DEBUG')

from aiohttp import ClientSession
from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.common.exceptions import AuthenticationException

from providers import LoggingProvider

logger = LoggingProvider.getLogger("server.main")

#import server

# Load environment variables (user/pass) from .env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# "RuntimeError: Event loop is closed" fix
# src: https://stackoverflow.com/a/45600858
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Connect to Xbox Live and set a global client variable
async def authenticate(loop):
    session = ClientSession(loop=loop)
    tokens_file_path = os.getenv("XBL_TOKENS_PATH")

    # Init the AuthenticationManager with a ClientSession, client id & secret
    auth_mgr = AuthenticationManager(
        session, client_id=os.getenv("XBL_CID"), client_secret=os.getenv("XBL_CSEC"), redirect_uri=""
    )

    # Attempt to load the authentication tokens from disk
    try:
        with open(tokens_file_path, mode="r") as f:
            tokens = f.read()
        auth_mgr.oauth = OAuth2TokenResponse.parse_raw(tokens)
    except FileNotFoundError:
        logger.error("Err loading tokens!")
        sys.exit(-1)
        
    # Attempt to refresh tokens if required
    try:
        await auth_mgr.refresh_tokens()
    except ClientResponseError:
        logger.error("Could not refresh tokens!")
        sys.exit(-1)
        
    # Save the refreshed tokens to disk
    with open(tokens_file_path, mode="w") as f:
        f.write(auth_mgr.oauth.json())
        logger.info("Saved refreshed tokens to disk!")
        
    # Init the XboxLiveClient
    xbl_client = XboxLiveClient(auth_mgr)

    xbl_client._xbl_web_api_lastauth = time.time()

    logger.info("Logged in as '%s' (%s) " % (
        xbl_client._auth_mgr.xsts_token.gamertag,
        xbl_client._auth_mgr.xsts_token.xuid
    ))

    #server.get_client(xbl_client)
    return xbl_client, session


if __name__ == '__main__':
    asyncio.run(authenticate())
