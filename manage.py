import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from bap import app
from bap import models
from scrape_periodic import parse_beer_positions


@app.shell_context_processor
def make_shall_context():
    return {
        "db": models.db,
        "User": models.User,
        "Post": models.Post,
        "BeerPosition": models.BeerPosition,
    }


@app.before_first_request
def init_scheduler():
    # ця штука запускалась двічі, тому варто винести в функцію і запускати
    # перед кожним перезавантаженням застосунку на Flask
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=parse_beer_positions, trigger="interval", minutes=1)
    scheduler.start()
    # вимикаємо заплановані задачі, якщо застосунок вимкнено
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(debug=True)