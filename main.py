import sys
import os

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.common.exceptions import AuthenticationException

import server

# Load environment variables (user/pass) from .env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# Connect to Xbox Live and set a global client variable
def authenticate():
    global auth_mgr
    auth_mgr = AuthenticationManager()
    auth_mgr.email_address = os.getenv("XBL_EMAIL")
    auth_mgr.password = os.getenv("XBL_PASS")
    # Attempt to login
    try:
        auth_mgr.authenticate(do_refresh=True)
    except AuthenticationException as e:
        print('Email/Password authentication failed! Err: %s' % e)
        sys.exit(-1)

    print('Logged in as: %s' % auth_mgr.userinfo.gamertag)

    # Create the XboxLiveClient
    xbl_client = XboxLiveClient(
        auth_mgr.userinfo.userhash, auth_mgr.xsts_token.jwt, auth_mgr.userinfo.xuid)

    server.get_client(xbl_client)


if __name__ == '__main__':
    authenticate()
