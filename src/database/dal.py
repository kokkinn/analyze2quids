import datetime
import enum
import logging

import pandas as pd
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.database.models import RawTransaction, EnhancedTransaction, PersonalCategoryRegex, BankAccount
from src.util import get_cost_from_str

BANK_NAME: str = 'nationwide'


class TransactionTypes(enum.Enum):
    IN: str = 'in'
    OUT: str = 'out'


def create_raw_transaction(db: Session,
                           date: str,
                           description: str,
                           paid_out: str,
                           paid_in: str,
                           card_name: str,
                           source: str,
                           filename: str,
                           location: str = None,
                           balance: str = None,
                           type: str = None,
                           ) -> None | RawTransaction:
    """
    Create a new transaction record in the database.
    """
    db_transaction = RawTransaction(
        date=date,
        type=type,
        description=description,
        paid_out=paid_out,
        paid_in=paid_in,
        balance=balance,
        location=location,
        card_name=card_name,
        source=source,
        filename=filename
    )

    checksum: str = RawTransaction.calculate_checksum(db_transaction)
    if existing := db.query(RawTransaction).filter_by(checksum=checksum).first():
        # print(f'{existing} already exists, ignoring...')
        return

    db_transaction.checksum = checksum
    db.add(db_transaction)
    db.commit()
    return db_transaction


def create_enhanced_transaction(db: Session, raw_transaction_id: int) -> None | EnhancedTransaction:
    """
    Create a new enhanced transaction record in the database.
    """
    from src.categories import get_categories_from_entity
    from src.categories import get_flow_from_raw_transaction
    try:
        raw_transaction = db.query(RawTransaction).filter_by(id=raw_transaction_id).first()
    except NoResultFound:
        logging.warning(
            f'RawTransaction with id {raw_transaction_id} does not exist, cannot create EnhancedTransaction')
        return
    category = get_categories_from_entity(raw_transaction.description)
    direction = TransactionTypes.IN.value if raw_transaction.paid_in else TransactionTypes.OUT.value
    db_transaction = EnhancedTransaction(
        date=datetime.datetime.strptime(raw_transaction.date, "%d %b %Y"),
        type=raw_transaction.type,
        entity=raw_transaction.description,
        category=category[-1] if category else 'UM',
        value=get_cost_from_str(raw_transaction.paid_in) if raw_transaction.paid_in else get_cost_from_str(
            raw_transaction.paid_out),
        flow=get_flow_from_raw_transaction(raw_transaction.description, raw_transaction.type, direction),
        direction=direction,
        location=raw_transaction.location,
        card_name=raw_transaction.card_name,
        balance=get_cost_from_str(raw_transaction.balance) if raw_transaction.balance else None,
        source=raw_transaction.source,
        raw_transaction_id=raw_transaction_id
    )

    db.add(db_transaction)
    db.commit()
    return db_transaction


def get_enhanced_transactions(db: Session, date_start: datetime = None, date_end: datetime = None) -> None | list[type[
    EnhancedTransaction]]:
    query = db.query(EnhancedTransaction)

    if date_start is not None:
        query = query.filter(EnhancedTransaction.date >= date_start)

    if date_end is not None:
        query = query.filter(EnhancedTransaction.date <= date_end)

    return query.order_by(EnhancedTransaction.date).all()


def get_enhanced_transactions_dataframe(db: Session, date_start: datetime = None,
                                        date_end: datetime = None) -> None | pd.DataFrame:
    query = db.query(EnhancedTransaction)

    if date_start is not None:
        query = query.filter(EnhancedTransaction.date >= date_start)

    if date_end is not None:
        query = query.filter(EnhancedTransaction.date <= date_end)

    query.order_by(EnhancedTransaction.date)

    df = pd.read_sql(query.statement, query.session.bind)

    return df


def get_all_personal_categories(db: Session) -> list[type[PersonalCategoryRegex]]:
    return db.query(PersonalCategoryRegex).all()


def get_all_bank_accounts(db: Session) -> list[type[BankAccount]]:
    return db.query(BankAccount).all()


def get_excluded_personal_categories(db: Session) -> list[type[PersonalCategoryRegex]]:
    return db.query(PersonalCategoryRegex).filter(PersonalCategoryRegex.hide == True).all()


def create_bank_account(db: Session, name_from_csv: str) -> None:
    if not db.query(BankAccount).filter_by(name_from_csv=name_from_csv).first():
        account = BankAccount(name_from_csv=name_from_csv)
        db.add(account)
        db.commit()
        print(f'Derived account {name_from_csv} from csv')
    else:
        print(f'Derived account {name_from_csv} already exists')
# from src.database.common import db_session
# print(get_excluded_personal_categories(db_session))

# create_raw_transaction(db_session, '25 Apr 2002', 'Type A', 'Description', '£10', '', '£ 20000')
# print(get_enhanced_transactions(db_session, datetime.datetime(2020, 1, 1), datetime.datetime(2025, 1, 2)))
