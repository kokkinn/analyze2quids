"""
Derives transactions categories
"""
import enum
from typing import Literal

import pandas as pd
import re
from src.database.common import db_session
from src.database.models import EnhancedTransaction, PersonalCategoryRegex, RawTransaction, BankAccount
from src.database.dal import get_all_personal_categories, get_all_bank_accounts
from pprint import pprint as pp
from collections import defaultdict

# df = pd.read_sql_query(q.statement, db_session.bind)
food_patterns: list[str] = [
    r'tesco', r'sainsbury\'s', r'mcdonalds', r'amazon fresh', r'wetherspoon',
    r'co-op', r'greggs', r'kebab', r'iceland', r'food', r'costa', r'coffee',
    r'domino\'s', r'wendy\'s', r'supermarket', r'restaurant', r'meat', r'halal',
    r'grocery', r'aldi', r'sainsburys', r'albina', r'grill', r'spoon', r't4',
    r'chopstick', r'oodles', r'minimarket', r'twg', r'caffe', r'franco manca',
    r'quick shop', r'super snax', r'snax', r'gdk', r'tortilla',
    r'bilmonte', r'chopstix',
    r'thirst soho', r'dines', r'original thai chi', r'faith wok chin',
    r'nisa local', r'poundland', r'crown & cushion', r'mleczko', r'YAGMUR', r'cex borehamwood', r'ja bee', r'nilgiri',
    r'simply local', 'poundstretcher', r'mission possible', r'casablanca', r'budgens', 'george street express',
    r'black sheep', r'netto kent', 'opa london', r'street greek', 'greek cuisine', 'swami convenience', 'pizza',
    'falafel', r'boxpark?',
]

CATEGORY_REGEX: dict[str, str] = {
    'accommodation': r'athena hotel|hotel',
    'adobe': r'adobe',
    'alcohol and pub': r'\bpub\b|\btavern\b|wine|alcohol|camden eye|spread eagle',
    'amazon': 'amazon',
    'apple_bill': r'apple\.com',
    'aws': r'aws',
    'charity': r'charity',
    'clothes': r'primark|marks&spencer|h & m|foot locker|british heart foundation|pah|st christophers|hewits of croydon',
    'driving learning': r'dvsa|dvla|reddriving',
    'education': r'hillel|course',
    'ebay': 'ebay',
    'entertainment and concerts': 'zoo|worlds end|bush empire',
    'food': '|'.join(food_patterns),
    'gadgets': r'apple store|gadget|laptop|argos',
    'health': r'pharmacy|st\. clare chemists|boots|wh smith|specsavers|savers health|dental',
    'gym': r'nuffield|the gym group|the gym ltd',
    'linkedin': r'linkedin',
    'music gear, merch, vinyls': r'feline guitars|shadowcast ltd|hmv|vinyl|merch|bandcamp|napalm',
    'transaction fee': 'transaction fee',
    'phone': r'^ee',
    'post office': r'post office',
    'postcards / photo / stationery / home': 'card factory|diy|snappy snaps|onebelow',
    'rehersal': r'mill hill music complex|pirate|the premises|rehersal',
    'rent': 'flatshare',
    'taxi': r'\btaxi\b|uber|bolt',
    'toys': 'lego',
    'transport': r'trainline|tfl|bus\b|redrose travel|swrailwayselfserve|sumup|swtrains|train',
}

personal_categories: list[type[PersonalCategoryRegex]] = get_all_personal_categories(db_session)
personal_bank_accounts: list[type[BankAccount]] = get_all_bank_accounts(db_session)
my_accounts_names_escaped: list[str] = [re.escape(str(ba.name_from_csv)) for ba in personal_bank_accounts]
personal_accounts_known_numbers = [re.search(r'\d{1,5}', ap).group(0) for ap in my_accounts_names_escaped]
accounts_number_escaped_pattern = '|'.join(personal_accounts_known_numbers)


class TransferTypes(enum.Enum):
    TRANSFER_TO: str = 'Transfer to'  # for debit
    TRANSFER_FROM: str = 'Transfer from'  # for debit
    CASH_CREDIT: str = 'Cash credit'  # withdrawal
    PAYMENT_TO: str = 'Payment to'  # transfers to ppl or personal credit card
    # "Bank Credit A B C" (type and description) for personal transfers in


# TODO manual category override at load stage?
# TODO AI driven regex adjustment with web search?
def get_categories_from_entity(entity: str) -> list[str | None]:
    res = []
    for pc in personal_categories:
        if re.search(str(pc.regex), entity, re.IGNORECASE):
            res.append(pc.category)
            return res
    for category, pattern in CATEGORY_REGEX.items():
        if re.search(pattern, entity, re.IGNORECASE):
            res.append(category)
    return res


def get_flow_from_raw_transaction(description: str, type_str: str, direction: str) -> Literal[
    'me2me', 'me2others', 'others2me', 'mepayment', 'refund']:
    if not type_str:
        type_str = description
    # if descriptions matches with any of derived accounts (from csv, start of etl)
    # print(accounts_number_escaped_pattern)
    # print(f'--{description}--, --{type_str}--, --{direction}--')
    if (
            description in ('PAYMENT RECEIVED -- THANKYOU', 'MEMBER CREDIT CARD')
            or description == TransferTypes.CASH_CREDIT.value
            or re.search(accounts_number_escaped_pattern, description)
            and type_str in (TransferTypes.TRANSFER_TO.value,
                             TransferTypes.TRANSFER_FROM.value,
                             TransferTypes.CASH_CREDIT.value)
    ):
        return 'me2me'
    elif direction == 'out' and type_str == TransferTypes.PAYMENT_TO.value:  # TODO filter the credit card from there
        return 'me2others'
    elif re.search(r'bank credit', type_str, re.IGNORECASE) and direction == 'in':
        return 'others2me'
    elif direction == 'in':
        return 'refund'
    else:
        return 'mepayment'


res = get_categories_from_raw_transaction = get_flow_from_raw_transaction('070806 32616116', 'Transfer to', 'out')
print(res)
# get_categories_from_entity()
# categorised = defaultdict(list)
# q = db_session.query(EnhancedTransaction)
# res = q.all()
# for r in res:
#     cs = get_categories_from_entity(r.entity)
#     if not cs:
#         categorised[None].append(r.entity)
#     for c in cs:
#         categorised[c].append(r.entity)
# pp(categorised)
