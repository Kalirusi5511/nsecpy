import copy
import re

import pytest
from aioresponses import aioresponses

from nsecpy import UnsupportedRegionError, regions
from nsecpy.listing import Game
from nsecpy.pricing import MAX_PRICES

from .sample_data import SAMPLE_GAME, SAMPLE_PRICE_RESPONSE


@pytest.mark.asyncio
async def test_pricing_from_game():
    with aioresponses() as m:
        # Build response without diffrent title id
        response = copy.deepcopy(SAMPLE_PRICE_RESPONSE)
        response['prices'][0]['title_id'] = 70010000036098

        m.get('https://api.ec.nintendo.com/v1/price?country=US&lang=en&ids=70010000036098', payload=response)

        game = Game(SAMPLE_GAME, regions['en_US'])
        price = await game.query_price()

        assert price
        assert price.discount_price.end > price.discount_price.start


@pytest.mark.asyncio
async def test_pricing_compare_discount():
    with aioresponses() as m:
        DISCOUNT_ID = 70010000039205
        NORMAL_ID = 7001000012345
        URL_BASE = 'https://api.ec.nintendo.com/v1/price?country=US&lang=en&ids='

        # Build Response without discount
        normal_response = copy.deepcopy(SAMPLE_PRICE_RESPONSE)
        normal_response['prices'][0].pop('discount_price')
        normal_response['prices'][0]['title_id'] = NORMAL_ID

        m.get(URL_BASE + str(DISCOUNT_ID), payload=SAMPLE_PRICE_RESPONSE)
        m.get(URL_BASE + str(NORMAL_ID), payload=normal_response)

        discount = await regions['en_US'].query_price(DISCOUNT_ID)
        normal = await regions['en_US'].query_price(NORMAL_ID)

        assert normal.region == discount.region
        assert normal.sales_status == discount.sales_status
        assert normal.regular_price == discount.regular_price
        assert normal.title_id == NORMAL_ID
        assert discount.title_id == DISCOUNT_ID
        assert discount.discount_price


@pytest.mark.asyncio
async def test_pricing_multiple():
    # Build responses
    START_ID = 70010000000000
    ids = [r for r in range(START_ID, START_ID + MAX_PRICES + 1)]  # MAX_PRICES + 1 items

    page1_ids = ids[:-1]  # First MAX_PRICES items
    page1_ids_str = ','.join([str(i) for i in page1_ids])
    page2_id = ids[-1]  # Last item

    page1_response = copy.deepcopy(SAMPLE_PRICE_RESPONSE)
    page1_response['prices'].pop(0)
    for id in page1_ids:
        item = copy.deepcopy(SAMPLE_PRICE_RESPONSE['prices'][0])
        item['title_id'] = id
        page1_response['prices'].append(item)

    page2_response = copy.deepcopy(SAMPLE_PRICE_RESPONSE)
    page2_response['prices'][0]['title_id'] = page2_id

    with aioresponses() as m:
        # Modern fix: Match any price URL to avoid parameter ordering issues in aioresponses
        pattern = re.compile(r"https://api\.ec\.nintendo\.com/v1/price\?.*")
        m.get(pattern, payload=page1_response)

        m.get(f'https://api.ec.nintendo.com/v1/price?country=US&lang=en&ids={page2_id}', payload=page2_response)

        lastPrice = None
        priceCount = 0

        async for price in regions['en_US'].query_prices(ids):
            if lastPrice:
                assert price.region == lastPrice.region
                assert price.sales_status == lastPrice.sales_status
                assert price.regular_price == lastPrice.regular_price
                assert price.discount_price == lastPrice.discount_price

            priceCount += 1
            lastPrice = price

        assert priceCount == len(ids)


@pytest.mark.asyncio
async def test_pricing_not_found():
    with aioresponses() as m:
        # Build not_found response data
        response = copy.deepcopy(SAMPLE_PRICE_RESPONSE)
        response['prices'][0].pop('regular_price')
        response['prices'][0].pop('discount_price')
        response['prices'][0]['sales_status'] = 'not_found'

        m.get('https://api.ec.nintendo.com/v1/price?country=US&lang=en&ids=70010000039205', payload=response)

        price = await regions['en_US'].query_price(70010000039205)
        assert price.sales_status == 'not_found'


@pytest.mark.asyncio
async def test_pricing_no_data():
    with aioresponses() as m:
        # Build not_found response data
        response = copy.deepcopy(SAMPLE_PRICE_RESPONSE)
        response['prices'].pop(0)

        m.get('https://api.ec.nintendo.com/v1/price?country=US&lang=en&ids=70010000039205', payload=response)

        price = await regions['en_US'].query_price(70010000039205)
        assert price is None


@pytest.mark.asyncio
async def test_pricing_invalid_region():
    for region in regions.values():
        if not region.supports_pricing:
            with pytest.raises(UnsupportedRegionError) as e_info:
                await region.query_price(70010000039205)

            return

    raise RuntimeError('Failed to find region with no pricing support')