"""
Data analysis module
"""
import datetime

from src.database.common import db_session

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.database.models import EnhancedTransaction
from src.database.dal import get_enhanced_transactions_dataframe


def run_analysis(date_start: datetime.datetime, date_end: datetime) -> None:
    """
    Displays graphs
    :param date_start: start date of analysis, inclusive
    :param date_end: end date of analysis, inclusive
    :return:
    """
    if not isinstance(date_start, datetime.datetime) or not isinstance(date_end, datetime.datetime):
        raise TypeError('date_start and date_end must be datetime objects')

    df = get_enhanced_transactions_dataframe(db_session, date_start, date_end)
    actual_start = df['date'].min().strftime('%b %d, %Y')
    actual_end = df['date'].max().strftime('%b %d, %Y')

    # Categories #############################
    # Frequency
    limit_to: int = 100
    categories_counts = df['category'].value_counts()  # series: category -> count
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories_counts.index[0:limit_to], categories_counts.values[0:limit_to], color='skyblue')
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  #
                     textcoords="offset points",
                     ha='center', va='bottom')
    plt.title('Categories and their Frequencies')
    plt.xticks(rotation=90)
    plt.xlabel('Categories')
    plt.ylabel('Frequencies')
    plt.tight_layout()
    plt.show()

    # Cost
    plt.figure(figsize=(16, 10))
    df['value'] = df['value'].astype(int)
    categories_total_cost = df.groupby('category')['value'].sum().sort_values(
        ascending=False)  # series: category -> cost
    bars = plt.bar(categories_total_cost.index[0:limit_to], categories_total_cost.values[0:limit_to], color='skyblue')
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  #
                     textcoords="offset points",
                     ha='center', va='bottom')
    plt.title(f'Categories and their Cost. \n{actual_start} to {actual_end}')
    plt.xticks(rotation=90)
    plt.xlabel('Categories')
    plt.ylabel('Total cost')
    plt.tight_layout()
    plt.show()
    ##########################################

    # Balance ################################
    # plt.figure(figsize=(10, 6))
    # plt.plot(df['date'], df['value'])
    # plt.show()
    #
    # only_positive = df[df['direction'] == 'in']
    # plt.plot(only_positive['date'].tolist(), only_positive['value'].cumsum())
    # plt.show()
    #
    # only_negative = df[df['direction'] == 'out']
    # plt.plot(only_negative['date'].tolist(), only_negative['value'].apply(lambda x: -x).cumsum())
    # plt.show()
    ##########################################
    # TODO Filter by categories / what if one to another card transaction ?


sd = datetime.datetime(2023, 4, 1)
ed = datetime.datetime(2024, 6, 3)
run_analysis(sd, ed)
