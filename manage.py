import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from bap import app
from bap import models

def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="interval", seconds=60)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.shell_context_processor
def make_shall_context():
    return {
        "db": models.db,
        "User": models.User,
        "Post": models.Post,
    }


if __name__ == '__main__':
    app.run(debug=True)