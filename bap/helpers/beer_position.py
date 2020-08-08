import pandas as pd
from datetime import datetime

from bap.models import BeerPosition


store_image_dict = {
    "megamarket": "https://zakaz.ua/static/images/store-tile-logos/megamarket.svg",
    "auchan": "https://zakaz.ua/static/images/store-tile-logos/auchan.svg",
    "metro": "https://zakaz.ua/static/images/store-tile-logos/metro.svg",
    "furshet": "https://zakaz.ua/static/images/store-tile-logos/furshet.svg",
    "novus": "https://zakaz.ua/static/images/store-tile-logos/novus.svg",
    "vostorg": "https://zakaz.ua/static/images/store-tile-logos/vostorg.svg",
    "tavriav": "https://zakaz.ua/static/images/store-tile-logos/tavriav.svg",
}


def load_for_index_page():
    results = BeerPosition.get_by_date(datetime.now().date())
    df = pd.DataFrame(map(prepare_record, results))
    ean_list = get_product_ean_available_in_count(df, threshold=3)

    agg_df = pd.DataFrame([get_beer_metadata(df, ean) for ean in ean_list]).sort_values(by="min_price")
    return agg_df.to_dict(orient="records")


def prepare_record(record):
    return record.__dict__.copy()


def get_product_ean_available_in_count(df, threshold: int = 2):
    count_df = df.groupby(by=["ean"]).price.count()
    ean_index = count_df[count_df >= threshold].index
    return ean_index.values


def get_beer_metadata(df, ean: str):
    sorted_df = df[df.ean == ean].sort_values(by="price")
    min_price_row = sorted_df.iloc[0]

    price_difference = [{
        "store": store,
        "diff": (price - min_price_row["price"]) / 100
    } for price, store in zip(sorted_df.price.values, sorted_df.source.values)]

    return {
        "title": min_price_row["title"],
        "img_url": min_price_row["img_url"],
        "min_price_store": min_price_row["source"],
        "store_img_url": store_image_dict[min_price_row["source"]],
        "min_price": min_price_row["price"] / 100,
        "price_difference": price_difference
    }


if __name__ == '__main__':
    load_for_index_page()