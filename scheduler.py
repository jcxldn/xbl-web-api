# Daily reAuth scheduler

from apscheduler.schedulers.background import BackgroundScheduler

import main

sched = BackgroundScheduler()


def setup():
    sched.add_job(timed_reauth)
    sched.start()


@sched.scheduled_job('interval', hours=1)
def timed_reauth():
    print('[Timed ReAuth] Authenticated: ' + str(main.auth_mgr.authenticated))
    if not main.auth_mgr.authenticated:
        print('[Timed ReAuth] Not authenticated, authenticating!')
        main.authenticate()
