import datetime
import logging

from bap import db
from bap.models import BeerPosition
from scraper.zakaz_ua import StoreID, parse_beer_data
from scraper.zakaz_ua import (
    FurshetBeerClient,
    MegaMarketBeerClient,
    MetroBeerClient,
    AuchanBeerClient,
    NovusBeerClient,
    TavriavBeerClient,
    VostorgBeerClient
)

log_level = logging.DEBUG
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=log_level, format=log_format)


def parse_beer_positions():
    parse_arguments = [
        (StoreID.furshet.name, FurshetBeerClient),
        (StoreID.metro.name, MetroBeerClient),
        (StoreID.megamarket.name, MegaMarketBeerClient),
        (StoreID.auchan.name, AuchanBeerClient),
        (StoreID.novus.name, NovusBeerClient),
        (StoreID.tavriav.name, TavriavBeerClient),
        (StoreID.vostorg.name, VostorgBeerClient),
    ]

    date = datetime.datetime.now().date()

    for source_name, client_class in parse_arguments:
        logging.info(f"Починаємо парсити дані для {source_name}")
        records = BeerPosition.get_by_date(date, source=source_name)

        if not len(records):
            df = parse_beer_data(source_name, source_client_class=client_class)
            db.session.add_all(
                [BeerPosition(**record) for record in df.to_dict(orient="records")]
            )
            db.session.commit()
            logging.info(f"Додано {df.shape[0]} записів до бази даних.")
        else:
            logging.info(f"Дані для {source_name.capitalize()} за {str(date)} вже додано")


if __name__ == '__main__':
    parse_beer_positions()