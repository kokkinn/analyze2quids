import csv
import os

import pandas as pd

from src.database.constants import NATIONWIDE_ENCODING, NATIONWIDE_META_ROWS_NUM


def get_clean_values_from_csv_row(row: str) -> list:
    return [v.replace('"', '').replace('\n', '').replace('\t', '') for v in row.split(',')]


def get_nationwide_meta_rows(rows: list[str]) -> dict[str, str] | None:
    expected_meta: tuple[str, str, str] = ('Account Name:', 'Account Balance:', 'Available Balance: ')
    res = {}
    for r in rows:
        a = r.split(',')
        if len(a) == 2:
            res[a[0].strip('"')] = a[1].strip('"').strip("\n")
    if expected_meta != tuple(res.keys()):
        print(f'WARNING. Invalid meta keys: {res}')
        return None
    return res


def validate_nationwide_csv(csv_path: str) -> bool:
    possible_columns_sets = {'credit': ('Date', 'Transactions', 'Location', 'Paid out', 'Paid in'),
                             'debit': ('Date', 'Transaction type', 'Description', 'Paid out', 'Paid in', 'Balance')}
    f = open(csv_path, 'r', encoding=NATIONWIDE_ENCODING)
    meta_rows = [next(f) for _ in range(NATIONWIDE_META_ROWS_NUM)]
    if not get_nationwide_meta_rows(meta_rows):
        return False
    next(f)
    headers = next(f)
    for cs in possible_columns_sets.values():
        if (ccs := tuple(get_clean_values_from_csv_row(headers))) == cs:
            return True
    print(f'Invalid column set: {ccs}')
    return False


def get_dataframe(csv_path: str) -> pd.DataFrame:
    """
    Returns dataframe read from file
    :param csv_path:
    :return: pd.DataFrame
    """
    # if not os.path.exists(csv_path):
    #     raise FileNotFoundError(f'CSV {csv_path} does not exist')
    return pd.read_csv(csv_path, skiprows=3, header=0, encoding=NATIONWIDE_ENCODING)


def get_nationwide_reader(csv_path: str) -> tuple[csv.DictReader, str, str]:
    csvfile = open(csv_path, 'r', encoding=NATIONWIDE_ENCODING)
    skip_rows: int = 3
    meta_data = get_nationwide_meta_rows([next(csvfile) for _ in range(skip_rows + 1)])
    return csv.DictReader(csvfile), meta_data['Account Name:'], csvfile.name.split('/')[-1]  # TODO OS specific?


# for filename in os.listdir('data'):
#     validate_nationwide_csv(f'data/{filename}')
#     break
