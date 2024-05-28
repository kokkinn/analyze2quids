import datetime
import logging
from sqlalchemy.orm import Session

from src.sqlalchemy import models


def create_raw_transaction(db: Session,
                           date: str,
                           transaction_type: str,
                           description: str,
                           paid_out: str,
                           paid_in: str,
                           balance: str,
                           ) -> None | models.RawTransaction:
    """
    Create a new transaction record in the database.
    """
    db_transaction = models.RawTransaction(date=datetime.datetime.strptime(date, '%d %b %Y'),
                                           transaction_type=transaction_type,
                                           description=description,
                                           paid_out=paid_out,
                                           paid_in=paid_in,
                                           balance=balance,
                                           )

    checksum: str = models.RawTransaction.calculate_checksum(db_transaction)
    if existing := db.query(models.RawTransaction).filter_by(checksum=checksum).first():
        logging.warning(f'{existing} already exists, ignoring...')
        return

    db_transaction.checksum = checksum
    db.add(db_transaction)
    db.commit()
    return db_transaction


from src.sqlalchemy.db import db_session

create_raw_transaction(db_session, '25 Apr 2002', 'Type A', 'Description', '£10', '', '£ 20000')
