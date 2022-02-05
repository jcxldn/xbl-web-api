from time import sleep, time
import signal
import os
import sys
import subprocess
import pytest

# Fixture to spin up the webserver
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

    # Make a note of the test start time
    epoch_start = int(time())

    print("running tests!")
    yield  # Run tests

    print(
        "tests completed! Waiting until server has been up for 5 mins to ensure that scheduled jobs run..."
    )

    # Wait until 5 minutes has elapsed to ensure that scheduled jobs run
    while int(time() - epoch_start < 300):
        continue
        # Continue to wait...

    # 5 minutes has passed! Let's continue...

    print("Tests finished! Sending SIGINT/CTRL+C")

    if os.name == "nt":
        # Windows does not support sigint
        p.send_signal(signal.CTRL_C_EVENT)
    else:
        p.send_signal(signal.SIGINT)

    p.wait()  # Wait for subprocess to gracefully exit
    print("DONE!")
