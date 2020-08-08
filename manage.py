import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from bap import app
from bap import models
from scrape_periodic import parse_beer_positions


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


scheduler = BackgroundScheduler()
scheduler.add_job(func=parse_beer_positions, trigger="interval", minutes=5)
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