"""
Main script for now. Should split later
"""
import os

from src.get_file import get_nationwide_reader
from src.sqlalchemy.constants import SOURCE
from src.sqlalchemy.dal import create_raw_transaction, create_enhanced_transaction
from src.sqlalchemy.db import db_session
from src.sqlalchemy.models import RawTransaction, EnhancedTransaction


def load_csv_to_raw_db(csv_path: str) -> None:
    count_none: int = 0
    count_total: int = 0

    # NATIONWIDE CSV file for Debit / Credit map to -> DAL function arguments as Field names
    nationwide_to_raw_transaction_map: dict[str, str] = {'Date': 'date', 'Transaction type': 'type',
                                                         # TODO  mix for debit and credit, maybe separate
                                                         'Description': 'description', 'Paid out': 'paid_out',
                                                         'Paid in': 'paid_in', 'Balance': 'balance',

                                                         'Transactions': 'description',
                                                         'Location': 'location'
                                                         }
    reader, card_name, fn = get_nationwide_reader(csv_path)
    for row in reader:
        rt = create_raw_transaction(
            db=db_session,
            source=SOURCE,
            filename=fn,
            card_name=card_name,
            **{nationwide_to_raw_transaction_map[k]: v for k, v in row.items()}
        )
        if not rt:
            count_none += 1
        count_total += 1
    print(f'Loaded {count_total - count_none}/{count_total} rows from "{csv_path}"')


def load_raw_to_enhanced_db():
    unprocessed_raw_transactions: list[RawTransaction] = db_session.query(RawTransaction).filter(
        ~RawTransaction.enhanced_transaction.any()).all()

    loaded_count = 0

    for raw_transaction in unprocessed_raw_transactions:
        if not raw_transaction.enhanced_transaction:
            create_enhanced_transaction(db_session, raw_transaction.id)
            loaded_count += 1
    print(f'Loaded {loaded_count} Raw Transactions to Enhanced table.')
    return loaded_count


# csv_name: str = 'data/Statement Download 2024-May-29 9-21-29.csv'
# print(get_reader(csv_name))

for filename in os.listdir('data'):
    load_csv_to_raw_db(f'data/{filename}')
    load_raw_to_enhanced_db()
