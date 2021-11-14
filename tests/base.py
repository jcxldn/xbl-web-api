from time import sleep
from aiohttp import ClientSession
import signal
import os
import sys
import subprocess
import pytest


class BaseTest:
    # Define class variable for making http requests
    session: ClientSession

    # Fixture to spin up the webserver
    @pytest.fixture(scope="session", autouse=True)
    def setup(self):
        # Have this process sigint
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        cwd = os.getcwd()
        exec = sys.executable

        should_run_coverage = os.environ.get("XBLAPI_RUN_COVERAGE") is "1"

        if should_run_coverage:
            args = [exec, "-m", "coverage", "run", "--timid", "server.py"]
        else:
            args = [exec, "server.py"]

        print("Starting '%s' in dir '%s'..." % (str(args), cwd))

        p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False, cwd=cwd)
        print("Waiting 30 seconds for server start")

        if should_run_coverage:
            print("Measuring code coverage, DO NOT connect debugger!")
        else:
            print("You may connect your debugger now.")

        sleep(30)  # Wait for the server to start

        print("running tests!")
        yield  # Run tests

        print("Tests finished! Sending SIGINT/CTRL+C")

        if os.name == "nt":
            # Windows does not support sigint
            p.send_signal(signal.CTRL_C_EVENT)
        else:
            p.send_signal(signal.SIGINT)

        p.wait()  # Wait for subprocess to gracefully exit
        print("DONE!")

    # Fixture to get a fresh client session for every test run
    @pytest.fixture(scope="function", autouse=True)
    async def create_session(self):
        # workaround so session is accessible to tests, see: https://github.com/pytest-dev/pytest/issues/3869#issuecomment-488276259
        type(self).session = ClientSession()
        yield
        # Close the session if it isn't already closed
        # eg. test fails so context is not released
        await self.session.close()
