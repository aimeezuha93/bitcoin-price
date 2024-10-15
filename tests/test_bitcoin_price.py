import os
import sys
import inspect
import pytest
import unittest
from dags.operators.EXT_bitcoin_price.EXT_bitcoin_price_operator import CoinGeckoHandler

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


@pytest.mark.usefixtures("test_etl")
class TestEndpoints(unittest.TestCase):

    def test_api_availability(self):
        credentials = {"url": "https://api.coingecko.com/api/v3",
                       "key": "CG-ViMvxvaFYjRwTdhdC85NYqxH", "headers": {"accept": "application/json"}}
        my_gecko = CoinGeckoHandler(credentials)
        status = my_gecko._get_api_status()
        code = status.status_code
        self.assertEqual(code, 200)

    def test_api_cryptocurrencies(self):
        credentials = {"url": "https://api.coingecko.com/api/v3",
                       "key": "CG-ViMvxvaFYjRwTdhdC85NYqxH", "headers": {"accept": "application/json"}}
        my_gecko = CoinGeckoHandler(credentials)
        status = my_gecko._get_cryptocurrencies()
        code = status.status_code
        self.assertEqual(code, 200)

    def test_api_cryptocurrencies(self):
        credentials = {"url": "https://api.coingecko.com/api/v3",
                       "key": "CG-ViMvxvaFYjRwTdhdC85NYqxH", "headers": {"accept": "application/json"}}
        my_gecko = CoinGeckoHandler(credentials)
        status = my_gecko._get_coin_price_by_range(
            "bitcoin", "usd", "1704088800", "1714456800")
        code = status.status_code
        self.assertEqual(code, 200)


if __name__ == '__main__':
    unittest.main()
