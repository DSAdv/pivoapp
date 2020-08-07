
def prepare_record(record):
    data = record.__dict__.copy()
    del data["_sa_instance_state"]
    return data


def get_product_ean_available_in_count(df, threshold: int = 2):
    count_df = df.groupby(by=["ean"]).price.count()
    ean_index = count_df[count_df >= threshold].index
    return ean_index.values


def get_beer_metadata(df, ean: str):
    sorted_df = df[df.ean == ean].sort_values(by="price")
    min_price_row = sorted_df.iloc[0]

    price_difference = [{
        "store": store,
        "diff": price - min_price_row["price"]
    } for price, store in zip(sorted_df.price.values, sorted_df.source.values)]

    return {
        "title": min_price_row["title"],
        "min_price_store": min_price_row["source"],
        "min_price": min_price_row["price"] / 100,
        "price_difference": price_difference
    }
