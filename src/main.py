"""
Main script for now. Should split later
"""
import csv
import os
from src.sqlalchemy.dal import create_raw_transaction
from src.sqlalchemy.db import db_session
import pandas as pd
import logging

NATIONWIDE_ENCODING: str = 'latin1'


def get_dataframe(csv_path: str) -> pd.DataFrame:
    """
    Returns dataframe read from file
    :param csv_path:
    :return: pd.DataFrame
    """
    # if not os.path.exists(csv_path):
    #     raise FileNotFoundError(f'CSV {csv_path} does not exist')
    return pd.read_csv(csv_path, skiprows=3, header=0, encoding=NATIONWIDE_ENCODING)


def get_reader(csv_path: str) -> csv.DictReader:
    csvfile = open(csv_path, 'r', encoding=NATIONWIDE_ENCODING)
    skip_rows: int = 3
    for _ in range(skip_rows + 1):
        next(csvfile)
    return csv.DictReader(csvfile)


def load_csv_to_raw_db(csv_path: str) -> None:
    count_none: int = 0
    count_total: int = 0
    nationwide_to_raw_transaction_map: dict[str, str] = {'Date': 'date', 'Transaction type': 'transaction_type',
                                                         'Description': 'description', 'Paid out': 'paid_out',
                                                         'Paid in': 'paid_in', 'Balance': 'balance'}
    reader = get_reader(csv_path)
    print('a')
    for row in reader:
        rt = create_raw_transaction(db=db_session, **{nationwide_to_raw_transaction_map[k]: v for k, v in row.items()})
        if not rt:
            count_none += 1
        count_total += 1
    print(f'Loaded {count_total-count_none}/{count_total} rows from "{csv_path}"')


csv_name: str = 'data/Statement Download 2024-May-22 22-44-36.csv'
load_csv_to_raw_db(csv_name)
