import json
import logging
import requests

from typing import List
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from fake_useragent import UserAgent

log_level = logging.DEBUG
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=log_level, format=log_format)


def requests_retry_session(retries: int = 7,
                           backoff_factor: float = 0.2,
                           status_forcelist: tuple = (400, 500, 502, 503, 504),
                           session: requests.Session = None) -> requests.Session:

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
