import requests
import logging
#import pandas as pd
from typing import Dict
from pathlib import Path
from sqlalchemy import text
#from config.queries import *
# from common.tools.dag_settings import get_dag_tmp_files_path, save_df_file
# from common.tools.database_connection import get_engine


class CoinGeckoHandler():
    def __init__(self, connection: Dict[str, str]) -> None:
        self.connection = connection

    def _put_request(self, endpoint: str):
        url = f"{self.connection['url']}/{endpoint}x_cg_demo_api_key={self.connection['key']}"
        logging.info(f"URL: {url}")
        headers = self.connection["headers"]
        response = requests.get(url, headers=headers)
        return response

    def _get_api_status(self):
        response = self._put_request("ping?")
        return response

    def _get_cryptocurrencies(self):
        response = self._put_request("coins/list?")
        return response

    def _get_coin_price_by_range(self, id: str, currency: str, start_date: str, end_date: str):
        response = self._put_request(
            f"coins/{id}/market_chart/range?vs_currency={currency}&from={start_date}&to={end_date}&")
        return response


class BitcoinHandler():
    def __init__(self, api_conn: Dict[str, str], db_conn: Dict[str, str]) -> None:
        self.api_conn = api_conn
        self.db_conn = db_conn
        self.gecko_api = CoinGeckoHandler(self.api_conn)
        self.engine = get_engine(**self.db_conn)

    def _get_bitcoin_id(self):
        results = self.gecko_api._get_cryptocurrencies()
        for result in results.json():
            if result["name"] == "Bitcoin":
                return result["id"]
            else:
                logging.info("The specified currency was not found")

    def _get_bitcoin_data(self, id: str):
        results = self.gecko_api._get_coin_price_by_range(
            id, "usd", "1704088800", "1714456800")
        results = results.json()
        df = pd.DataFrame(results["prices"], columns=["date", "price"])
        return df

    def _put_sql_objects(self):
        with self.engine.begin() as conn:
            try:
                logging.info("Creating schema.")
                conn.execute(text(query_schema))
                logging.info("Creating 1st table.")
                conn.execute(text(query_table))
                logging.info("Creating 2nd table.")
                conn.execute(text(query_table_avg))
                conn.execute(text("COMMIT;"))
            except Exception as e:
                logging.info(f"Postgres Error: {e}")
            finally:
                conn.close()

    def _put_to_sql(self, id: str, dag_main_file: str):
        df = self._get_bitcoin_data(id)
        df.to_sql(
            "quarter_prices",
            self.engine,
            schema="bitcoin",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

        path_tmp = (
            f"{get_dag_tmp_files_path(dag_main_file)}{Path(dag_main_file).stem}/"
        )

        file_config = {}
        file_config["tmp_path"] = save_df_file(path_tmp, "df", df)
        return file_config

    def _calculate_moving_average(self, file_config: Dict[str, str]):
        # df = pd.read_pickle(file_config["tmp_path"])
        # df["moving_average"] = df["price"].rolling(window=5).mean()
        # df["date"] = (pd.to_datetime(df["date"], unit="ms"))

        df.to_sql(
            "moving_average",
            self.engine,
            schema="bitcoin",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
