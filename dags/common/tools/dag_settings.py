import json
import os
import logging
from datetime import timedelta


def get_current_file_execution(file, extension=False):
    if not extension:
        name = ((file.split("."))[0]).split("/")[-1]
    else:
        name = (file).split("/")[-1]
    return name


def get_dag_config(file_name):
    return json.load(
        open(
            f"{os.path.abspath(os.path.dirname(file_name))}/config/{get_current_file_execution(file_name)}_dev.json"
        )
    )


def get_schedule_interval(config):
    if isinstance(config, int):
        config = timedelta(seconds=config)
    return config


def get_dag_tmp_files_path(file_name):
    return f"{os.path.abspath(os.path.dirname(file_name))}/tmp_files/"


def save_df_file(path, file_name, dataframe):
    os.makedirs(path, mode=0o0777, exist_ok=True)
    file_path = f"{path}/{file_name}"
    dataframe.to_pickle(file_path)
    os.chmod(file_path, 0o0777)
    logging.info(f"file save on path {file_path}")
    return file_path
