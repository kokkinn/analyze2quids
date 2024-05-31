"""
Data analysis module
"""
import datetime

from src.sqlalchemy.db import db_session

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.sqlalchemy.models import EnhancedTransaction


def run_analysis(start_date: datetime.datetime, end_date: datetime) -> None:
    """
    Displays graphs
    :param start_date: start date of analysis, inclusive
    :param end_date: end date of analysis, inclusive
    :return:
    """
    if not isinstance(start_date, datetime.datetime) or not isinstance(end_date, datetime.datetime):
        raise TypeError('start_date and end_date must be datetime objects')

    query = db_session.query(EnhancedTransaction).filter(
        EnhancedTransaction.date >= start_date,
        EnhancedTransaction.date <= end_date).order_by(EnhancedTransaction.date)

    df = pd.read_sql(query.statement, query.session.bind)

    # Categories #############################
    # categories_counts = df['entity'].value_counts()
    # plt.figure(figsize=(10, 6))
    # plt.bar(categories_counts.index, categories_counts.values, color='skyblue')
    # plt.title('Categories and their Frequencies')
    # plt.xticks(rotation=90)
    # plt.xlabel('Categories')
    # plt.ylabel('Frequencies')
    # plt.show()
    ##########################################

    # Balance ################################
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['value'])
    plt.show()

    only_positive = df[df['direction'] == 'in']
    plt.plot(only_positive['date'].tolist(), only_positive['value'].cumsum())
    plt.show()

    only_negative = df[df['direction'] == 'out']
    plt.plot(only_negative['date'].tolist(), only_negative['value'].apply(lambda x: -x).cumsum())
    plt.show()
    ##########################################
    # TODO Filter by categories / what if one to another card transaction ?


sd = datetime.datetime(2023, 4, 1)
ed = datetime.datetime(2024, 5, 3)
run_analysis(sd, ed)
