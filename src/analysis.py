"""
Data analysis module
"""
import datetime
import random
from typing import Literal

from src.categories import CATEGORY_REGEX
from src.database.common import db_session
import matplotlib.dates as mdates
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.database.models import EnhancedTransaction
from src.database.dal import get_enhanced_transactions_dataframe, get_excluded_personal_categories


def draw_categories_chart(df: pd.DataFrame, chart_type: Literal['frequency', 'value'], limit_to: int = 10,
                          title: str = None) -> None:
    actual_start = df['date'].min().strftime('%b %d, %Y')
    actual_end = df['date'].max().strftime('%b %d, %Y')

    plt.figure(figsize=(10, 6) if chart_type == 'frequency' else (16, 10))

    if chart_type == 'frequency':
        categories_counts = df['category'].value_counts().head(limit_to)
        bars = plt.bar(categories_counts.index, categories_counts.values, color='skyblue')
    else:
        categories_total_cost = df.groupby('category')['value'].sum().sort_values(ascending=False).head(limit_to)
        bars = plt.bar(categories_total_cost.index, categories_total_cost.values, color='skyblue')
        total = sum(categories_total_cost.values)
        plt.annotate(f'Total value: {total}', xy=(0.85, 0.9), xycoords='axes fraction')

    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')

    plt.title(
        f"{title if title else f'Categories and their {chart_type.capitalize()}'}\n{actual_start} to {actual_end}")
    plt.xticks(rotation=90)
    plt.xlabel('Categories')
    plt.ylabel(chart_type.capitalize())
    plt.tight_layout()
    plt.show()


def draw_transactions_over_time(df: pd.DataFrame, categories: str | list[str], direction: str) -> None:
    if not categories:
        raise ValueError("No categories provided")
    if isinstance(categories, str):
        categories = [categories]
    if direction not in ('in', 'out'):
        raise ValueError(f"Direction must be either 'in' or 'out'. Got {direction}")

    caf: int = 500  # ceil and floor to
    total: int = 0
    # colors: list[str] = ['blue', 'green', 'purple', 'pink', 'black']
    # markers: list[str] = ['o', 'v', '^', 'd', 'x', 'D']

    markers = [
                  '.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd',
                  '|', '_'
              ] * 2

    colors = [
                 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan',
                 'navy', 'teal'
             ] * 2

    plt.figure(figsize=(25, 10))
    min_value, max_value = 0, 0

    for c in categories:
        transactions = df[
            (df['category'] == c)
            & (df['direction'] == direction)
            # & (df['flow'] == 'others2me')
            ]
        if transactions.empty:
            raise ValueError(f"No transactions found for category '{c}'")
        total += transactions['value'].sum()
        min_value = min(transactions['value'].min(), min_value)
        max_value = max(transactions['value'].max(), max_value)

        # min_value = min(math.floor(transactions['value'].min() / caf) * caf, min_value)
        # max_value = max(math.ceil(transactions['value'].max() / caf) * caf, max_value)

        plt.scatter(transactions['date'], transactions['value'],
                    color=colors.pop(random.randint(0, len(colors) - 1)),
                    s=20,
                    marker=markers.pop(random.randint(0, len(markers) - 1)),
                    label=c)

    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))

    plt.legend(loc='upper left')
    caf = 10
    num_ticks = 11
    plt.yticks(np.linspace(math.floor(min_value / caf) * caf, math.ceil(max_value / caf) * caf, num_ticks))
    plt.title(f'Transactions "{direction}" for {", ".join(categories)} over time')
    plt.xlabel('Date')
    plt.ylabel('Value of transactions')
    plt.xticks(rotation=45)
    # plt.tight_layout()
    plt.figtext(0.75, 0.89, f'Total value: £{total}', fontsize='large')
    plt.show()


def draw_balance_over_time(df: pd.DataFrame):
    df_sorted = df.sort_values(by='date', ascending=True)
    df_sorted.loc[df['direction'] == 'out', 'value'] *= -1
    balance = df_sorted['value'].cumsum()
    plt.figure(figsize=(10, 6))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    plt.plot(df_sorted['date'], balance)
    plt.xticks(rotation=45)
    plt.title('Balance over time')
    plt.show()


def run_analysis(date_start: datetime.datetime, date_end: datetime) -> None:
    """
    Displays graphs
    :param date_start: start date of analysis, inclusive
    :param date_end: end date of analysis, inclusive
    :return:
    """
    if not isinstance(date_start, datetime.datetime) or not isinstance(date_end, datetime.datetime):
        raise TypeError('date_start and date_end must be datetime objects')

    limit_to: int = 30
    exclude_categories: list[str] = [str(pc.category) for pc in get_excluded_personal_categories(db_session)]
    df = get_enhanced_transactions_dataframe(db_session, date_start, date_end)
    if df.empty:
        print(f'WARNING. Dataframe is empty: {df}, exiting...')
        return
    df['value'] = df['value'].astype(int)
    df = df[~df['category'].isin(exclude_categories)]
    df = df[(df['flow'] != 'me2me') & (df['flow'] != 'refund')]

    # income specific
    # draw_transactions_over_time(df, ['food'], 'out')
    #################

    # category
    # df_expenses, df_incomes = df[df['direction'] == 'out'], df[df['direction'] == 'in']
    # draw_categories_chart(df_expenses, chart_type='frequency', limit_to=limit_to,
    #                       title=f'Top {limit_to} frequent categories')
    # draw_categories_chart(df_expenses, chart_type='value', limit_to=limit_to,
    #                       title=f'Top {limit_to} most expensive categories')
    # draw_categories_chart(df_incomes, chart_type='value', limit_to=limit_to, title=f'Top {limit_to} sources of income')
    #########

    # Balance over time
    draw_balance_over_time(df)
    ###################

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
