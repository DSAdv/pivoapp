import json
import pandas as pd
import datetime
import pathlib
import logging
import requests

from typing import List
from enum import Enum, auto

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from fake_useragent import UserAgent

log_level = logging.DEBUG
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=log_level, format=log_format)


class StoreID(Enum):
    """  Цей клас дозволяє отримати ключі того чи іншого магазину.
         Також є можливість скористатись назвою атрибуту, наприклад: StoreID.metro.name
    """
    furshet = 0
    auchan = auto()
    novus = auto()
    megamarket = auto()
    metro = auto()
    tavriav = auto()
    vostorg = auto()


def requests_retry_session(retries: int = 7,
                           backoff_factor: float = 0.2,
                           status_forcelist: tuple = (400, 500, 502, 503, 504),
                           session: requests.Session = None) -> requests.Session:
    """  Метод додає функціональність для повторних спроб під час процесу скрапингу.
         Використовується як альтернатива request.get. Також перевизначені заголовки дозволяють
         імітувати поведінку браузера, що дозволяє надійніше виконувати потрібну роботу.
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    session.headers.update({
        "User-Agent": UserAgent().random,
        "Accept": "text/html,*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,mt;q=0.6,uk;q=0.5",
        "Content-Type": "application/json; charset=utf-8",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
    })
    return session


class BaseZakazBeerClient:
    store_id: id = None
    category_name: str = None

    def __init__(self,
                 session: requests.Session = None,
                 retries: int = 7):
        self.session = requests_retry_session(retries=retries, session=session)

    def fetch_goods(self, page: int = 1) -> List[dict]:
        params = {"page": page}
        response = self.session.get(self.get_api_url(), params=params)
        goods = response.json()["results"]
        logging.info(f"Отримано {len(goods)} товарів з параметрами: {json.dumps(params, indent=4)}")
        return goods

    @staticmethod
    def process_listing_position(position_data: dict) -> dict:
        record = position_data.copy()

        keys_for_remove = (
            "img", "gallery", "bundle", "unit", "currency", "discount", "is_hit",
            "in_stock", "producer", "custom_ribbons", "fat", "shelf_life", "temperature_range",
            "pack_amount", "horeca_only", "excisable", "price_wholesale", "restrictions"
        )

        record["discount_diff"] = record["discount"]["old_price"] - record["price"]
        record["is_discount"] = bool(record["discount_diff"])
        record["img_url"] = record["img"]["s1350x1350"]

        for key in keys_for_remove:
            del record[key]

        return record

    @classmethod
    def get_api_url(cls) -> str:
        return f"https://stores-api.zakaz.ua/stores/{cls.store_id}/categories/{cls.category_name}/products"


class FurshetBeerClient(BaseZakazBeerClient):
    store_id = 48215518
    category_name = "beer-furshet"


class AuchanBeerClient(BaseZakazBeerClient):
    store_id = 48246401
    category_name = "beer-auchan"


class NovusBeerClient(BaseZakazBeerClient):
    store_id = 48201070
    category_name = "beer"


class MegaMarketBeerClient(BaseZakazBeerClient):
    store_id = 48267601
    category_name = "beer-megamarket"


class MetroBeerClient(BaseZakazBeerClient):
    store_id = 48215611
    category_name = "beer-metro"


class TavriavBeerClient(BaseZakazBeerClient):
    """Можна використовувати лише в Харкові"""
    store_id = 48221130
    category_name = "beer-tavriav"


class VostorgBeerClient(BaseZakazBeerClient):
    """Можна використовувати лише в Харкові"""
    store_id = 48231001
    category_name = "beer-vostorg"


def parse_beer_data(source_name: str,
                    source_client_class: BaseZakazBeerClient,
                    session: requests.Session = None):
    store_client = source_client_class(session=session)
    beer_positions = list()
    more_flag = True
    page = 1

    logging.info(f"Починаємо скрапити дані з допомогою {store_client.__class__}...")

    # витягуємо дані через АРІ
    while more_flag:
        goods = store_client.fetch_goods(page=page)
        if goods:
            beer_positions.extend(goods)
            page += 1
        else:
            break

    clean_beer_positions = list(map(store_client.process_listing_position, beer_positions))
    logging.info(f"... отримано {len(clean_beer_positions)} позицій з пивом.")

    df = pd.DataFrame(clean_beer_positions)
    df["ingredients"] = df["ingredients"].map(json.dumps)
    df["nutrition_facts"] = df["nutrition_facts"].map(json.dumps)
    df["timestamp"] = datetime.datetime.utcnow()
    df["source"] = source_name

    return df[~df.volume.isna()]


def get_filename(source_name: str):
    now_date = datetime.datetime.now().strftime("%m-%d-%YT%H-%M-%S")
    return f"{source_name}_{now_date}_beer.csv"
