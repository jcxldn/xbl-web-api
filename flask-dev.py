# run this script to use Flask as the web server.

# only use this in development
# flask is NOT suitable in a production environment

import os
import asyncio
import coloredlogs

# Setup logging
coloredlogs.install(level='DEBUG')

import main
import server

async def flask_main():
    # auth with Xbox Live
    await main.authenticate()

    # start the flask server
    port = os.getenv("PORT") or 3000
    server.app.run(host='0.0.0.0', port=port)

asyncio.run(flask_main())
