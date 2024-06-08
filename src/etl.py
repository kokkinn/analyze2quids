"""
Main script for now. Should split later
"""
import os

from src.get_file import get_nationwide_reader
from src.database.constants import SOURCE
from src.database.dal import create_raw_transaction, create_enhanced_transaction, get_enhanced_transactions, \
    create_bank_account
from src.database.common import db_session
from src.database.models import RawTransaction, EnhancedTransaction
from src.categories import get_categories_from_entity, get_flow_from_raw_transaction


def load_csv_to_raw_db(csv_path: str) -> None:
    print('Loading CSV file to raw_transactions_tb')
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
    create_bank_account(db_session, card_name)
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


def load_raw_to_enhanced_db() -> int:
    """
    Loads raw transactions from raw_transactions_tb to enhanced_transactions_tb. Driven by raw transactions tha that are
    not linked to an enhanced one.
    :return:
    """
    print('Loading raw transactions from raw_transactions_tb to enhanced_transactions_tb')
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

def assign_categories_to_unmapped() -> int:
    """
    Tries to derive category for enhanced transactions that are unmapped.
    :return: Number of enhanced transactions changed
    """
    changed: int = 0
    enhanced_transactions = get_enhanced_transactions(db_session)
    for e in enhanced_transactions:
        if e.category == 'UM':
            if category := get_categories_from_entity(e.entity):
                e.category = category[-1]
                changed += 1
    db_session.commit()
    print(f'Changed categories count: {changed}')
    return changed


def reassign_all_categories(and_flows: bool = False) -> int:
    count: int = 0
    enhanced_transactions = get_enhanced_transactions(db_session)
    for e in enhanced_transactions:
        category = get_categories_from_entity(e.entity)
        e.category = category[-1] if category else 'UM'
        if and_flows:
            e.flow = get_flow_from_raw_transaction(e.entity, e.type, e.direction)
        count += 1
    db_session.commit()
    print(f'Changed categories count: {count}')
    return count


# for filename in os.listdir('data'):
#     load_csv_to_raw_db(f'data/{filename}')
# load_raw_to_enhanced_db()

# assign_categories_to_unmapped()
reassign_all_categories(and_flows=True)
