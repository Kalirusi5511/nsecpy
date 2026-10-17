from dataclasses import dataclass, field
from datetime import datetime
from os import execlp  # for typehinting
from typing import TYPE_CHECKING, Generator, List, Literal, Optional, Union

import aiohttp
import dateparser

from .exceptions import UnsupportedRegionError

MAX_PRICES = 50  # Maximum prices per query

if TYPE_CHECKING:
    from .listing import Game  # pragma: no cover
    from .regions import Region  # pragma: no cover


@dataclass
class Price:
    amount: str = None
    currency: str = None
    raw_value: str = None

    def __init__(self, data) -> None:
        self.amount = data['amount']
        self.currency = data['currency']
        self.raw_value = data['raw_value']


@dataclass
class DiscountPrice(Price):
    start: datetime = None
    end: datetime = None

    def __init__(self, data) -> None:
        tzsettings = {'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
        self.start = dateparser.parse(data['start_datetime'], settings=tzsettings)
        self.end = dateparser.parse(data['end_datetime'], settings=tzsettings)
        super().__init__(data)


@dataclass
class PriceQuery:
    region: "Region" = None
    sales_status: Literal["onsale", "sales_termination", "not_found"] = None
    title_id: int = None
    regular_price: Optional[Price] = None
    discount_price: Optional[DiscountPrice] = None

    def __init__(self, data, region) -> None:
        self.region = region
        self.sales_status = data['sales_status']
        if data.get('title_id'):
            self.title_id = data['title_id']
        if data.get('regular_price'):
            self.regular_price = Price(data['regular_price'])
        if data.get('discount_price'):
            self.discount_price = DiscountPrice(data['discount_price'])


async def query_price(region: "Region", game: Union[int, "Game"]) -> PriceQuery:
    price = [g async for g in query_prices(region, [game])]
    return price[0] if price else None


async def query_prices(region: "Region", games: List[Union[int, "Game"]]) -> Generator[PriceQuery, None, None]:
    if not region.supports_pricing:
        raise UnsupportedRegionError("Region does not support listings")

    lang, reg = region.culture_code.split('_')
    ids = [g if isinstance(g, int) else g.id for g in games]  # Convert games to their id
    groups = [ids[o : (o + MAX_PRICES)] for o in range(0, len(games), MAX_PRICES)]  # Put games in groups of MAX_PRICES

    async with aiohttp.ClientSession() as session:
        for group in groups:
            ids_str = ','.join([str(id) for id in group])
            url = f"https://api.ec.nintendo.com/v1/price?country={reg}&lang={lang}&ids={ids_str}"
            async with session.get(url) as request:
                request.raise_for_status()
                data = await request.json()

                for price in data['prices']:
                    yield PriceQuery(price, region)
