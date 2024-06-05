"""
Data analysis module
"""
import datetime
from typing import Literal
from src.database.common import db_session

import pandas as pd
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


def run_analysis(date_start: datetime.datetime, date_end: datetime) -> None:
    """
    Displays graphs
    :param date_start: start date of analysis, inclusive
    :param date_end: end date of analysis, inclusive
    :return:
    """
    if not isinstance(date_start, datetime.datetime) or not isinstance(date_end, datetime.datetime):
        raise TypeError('date_start and date_end must be datetime objects')

    limit_to: int = 10
    exclude_categories: list[str] = [str(pc.category) for pc in get_excluded_personal_categories(db_session)]
    df = get_enhanced_transactions_dataframe(db_session, date_start, date_end)
    df['value'] = df['value'].astype(int)
    if df.empty:
        print(f'WARNING. Dataframe is empty: {df}, exiting...')
        return
    df = df[~df['category'].isin(exclude_categories)]
    df_expenses, df_incomes = df[(df['direction'] == 'out') & (df['category'] != 'personal card2card')], df[
        df['direction'] == 'in']
    draw_categories_chart(df_expenses, chart_type='frequency', limit_to=limit_to,
                          title=f'Top {limit_to} frequent categories')
    draw_categories_chart(df_expenses, chart_type='value', limit_to=limit_to,
                          title=f'Top {limit_to} most expensive categories')
    draw_categories_chart(df_incomes, chart_type='value', limit_to=limit_to, title=f'Top {limit_to} sources of income')

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
