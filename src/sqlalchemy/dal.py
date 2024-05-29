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
                           transaction_type: str,
                           description: str,
                           paid_out: str,
                           paid_in: str,
                           balance: str,
                           ) -> None | RawTransaction:
    """
    Create a new transaction record in the database.
    """
    db_transaction = RawTransaction(date=date,
                                    transaction_type=transaction_type,
                                    description=description,
                                    paid_out=paid_out,
                                    paid_in=paid_in,
                                    balance=balance,
                                    source=BANK_NAME
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
        type=raw_transaction.transaction_type,
        entity=raw_transaction.description,
        value=get_cost_from_str(raw_transaction.paid_in) if raw_transaction.paid_in else get_cost_from_str(
            raw_transaction.paid_out),
        direction=TransactionTypes.IN.value if raw_transaction.paid_in else TransactionTypes.OUT.value,
        balance=get_cost_from_str(raw_transaction.balance),
        source=raw_transaction.source,
        raw_transaction_id=raw_transaction_id
    )

    db.add(db_transaction)
    db.commit()
    return db_transaction

# from src.sqlalchemy.db import db_session
# create_raw_transaction(db_session, '25 Apr 2002', 'Type A', 'Description', '£10', '', '£ 20000')
