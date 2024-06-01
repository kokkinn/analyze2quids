import datetime
import enum
import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.sqlalchemy.models import RawTransaction, EnhancedTransaction
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
        print(f'{existing} already exists, ignoring...')
        return

    db_transaction.checksum = checksum
    db.add(db_transaction)
    db.commit()
    return db_transaction


def create_enhanced_transaction(db: Session, raw_transaction_id: int) -> None | EnhancedTransaction:
    """
    Create a new enhanced transaction record in the database.
    """

    try:
        raw_transaction = db.query(RawTransaction).filter_by(id=raw_transaction_id).first()
    except NoResultFound:
        logging.warning(
            f'RawTransaction with id {raw_transaction_id} does not exist, cannot create EnhancedTransaction')
        return

    db_transaction = EnhancedTransaction(
        date=datetime.datetime.strptime(raw_transaction.date, "%d %b %Y"),
        type=raw_transaction.type,
        entity=raw_transaction.description,
        value=get_cost_from_str(raw_transaction.paid_in) if raw_transaction.paid_in else get_cost_from_str(
            raw_transaction.paid_out),
        direction=TransactionTypes.IN.value if raw_transaction.paid_in else TransactionTypes.OUT.value,
        location=raw_transaction.location,
        balance=get_cost_from_str(raw_transaction.balance) if raw_transaction.balance else None,
        source=raw_transaction.source,
        raw_transaction_id=raw_transaction_id
    )

    db.add(db_transaction)
    db.commit()
    return db_transaction

# from src.sqlalchemy.db import db_session
# create_raw_transaction(db_session, '25 Apr 2002', 'Type A', 'Description', '£10', '', '£ 20000')
