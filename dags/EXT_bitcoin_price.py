from datetime import timedelta
from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task
from airflow.exceptions import AirflowFailException
from common.tools.dag_settings import (
    get_dag_config,
    get_current_file_execution,
    get_schedule_interval
)
from operators.EXT_bitcoin_price.EXT_bitcoin_price_operator import CoinGeckoHandler, BitcoinHandler


CONFIG = get_dag_config(__file__)
CONFIG["default_args"]["retry_delay"] = timedelta(seconds=30)

with DAG(
    get_current_file_execution(__file__),
    default_args=CONFIG["default_args"],
    schedule_interval=get_schedule_interval(CONFIG["schedule_interval"]),
    catchup=False
) as dag:

    api_conn = CONFIG["api"]
    db_conn = CONFIG["db"]

    _start = EmptyOperator(task_id="start")

    @task(do_xcom_push=False)
    def healthcheck_api(api_conn):
        status = CoinGeckoHandler(api_conn)._get_api_status()
        if status.status_code != 200:
            raise AirflowFailException("Connection to Gecko API FAILED.")

    _healthcheck_api = healthcheck_api(api_conn)

    @task
    def create_sql_objects(api_conn, db_conn):
        BitcoinHandler(api_conn, db_conn)._put_sql_objects()

    _create_sql_objects = create_sql_objects(api_conn, db_conn)

    @task
    def get_bitcoin_id(api_conn, db_conn):
        return BitcoinHandler(api_conn, db_conn)._get_bitcoin_id()

    _get_bitcoin_id = get_bitcoin_id(api_conn, db_conn)

    @task
    def put_bitcoin_data(api_conn, db_conn, id, dag_main_file):
        return BitcoinHandler(api_conn, db_conn)._put_to_sql(id, dag_main_file)

    _put_bitcoin_data = put_bitcoin_data(
        api_conn, db_conn, _get_bitcoin_id, __file__)

    @task
    def get_moving_average(api_conn, db_conn, file_config):
        BitcoinHandler(api_conn, db_conn)._calculate_moving_average(
            file_config)

    _get_moving_average = get_moving_average(api_conn, db_conn, _put_bitcoin_data)

    chain(
        _start,
        _healthcheck_api,
        _create_sql_objects,
        _get_bitcoin_id,
        _put_bitcoin_data,
        _get_moving_average
    )
