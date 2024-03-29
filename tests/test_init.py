from time import sleep
import aiohttp
import signal
import os
import sys
import subprocess
import pytest


session: aiohttp.ClientSession


@pytest.fixture(scope="session", autouse=True)
def setup():
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


@pytest.fixture(scope="function", autouse=True)
async def createSession():
    print("Creating session...")
    global session
    session = aiohttp.ClientSession()
    yield
    # Close the session if it isn't already closed
    # eg. test fails so context is not released
    await session.close()


@pytest.mark.asyncio
async def test_index():
    async with session.get("http://localhost:3000") as res:
        assert res.status == 200
        assert res.content_type == "text/html"


@pytest.mark.asyncio
async def test_readme():
    async with session.get("http://localhost:3000/readme") as res:
        assert res.status == 200
        assert res.content_type == "text/markdown"
        assert (
            str(await res.text()).replace("\r", "")
            == open("README.md", mode="r").read()
        )


@pytest.mark.asyncio
async def test_info():
    async with session.get("http://localhost:3000/info") as res:
        assert res.status == 200
        assert res.content_type == "application/json"
        # Code copied from server.py when env var not available
        assert (await res.json())["sha"] == str(
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
        ).split("'")[1::2][0]
