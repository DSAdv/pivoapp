import datetime
from pytrends.request import TrendReq


KEYWORDS_LIST = {
    "пиво": "beer",
    "водка": "vodka",
    "вино": "wine",
    "коньяк": "cognac",
    "виски": "whiskey"
}

ALCOHOL_CATEGORY = 277
GEO = "UA"


def get_historical_data():
    current_date = datetime.datetime.now().date()
    month_start = (current_date - datetime.timedelta(days=30)).month

    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=0.1)
    data = pytrends.get_historical_interest(keywords=KEYWORDS_LIST,
                                            cat=ALCOHOL_CATEGORY,
                                            geo=GEO,
                                            year_start=current_date.year,
                                            year_end=current_date.year,
                                            day_end=31,
                                            month_start=month_start,
                                            month_end=current_date.month)
    return data