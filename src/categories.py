"""
Derives transactions categories
"""

import pandas as pd
import re
from src.sqlalchemy.db import db_session
from src.sqlalchemy.models import EnhancedTransaction
from pprint import pprint as pp
from collections import defaultdict

# df = pd.read_sql_query(q.statement, db_session.bind)

CATEGORY_REGEX: dict[str, str] = {
    'amazon': 'amazon',
    'ebay': 'ebay',
    'food': r'tesco|sainsbury\'s|mcdonalds|amazon fresh|wetherspoon|co-op|greggs|kebab|iceland|food|costa|coffee|domino\'s|wendy\'s|supermarket|restaurant|meat|halal|grocery|aldi|sainsburys|albina|grill|spoon|t4|chopstick|oodles|minimarket|twg|caffe',
    'transport': r'trainline|tfl|bus\b|redrose travel',
    'clothes': r'primark|marks&spencer|h & m|foot locker',
    'gym': r'nuffield|the gym group|the gym ltd',
    'apple_bill': r'apple\.com',
    'pharmacy': r'pharmacy',
    'taxi': r'taxi|uber|bolt',
    'paypal': r'paypal',
    'aws': r'aws',
    'gadgets': r'apple store|gadget|laptop',
    'phone': r'ee',
    'driving learning': r'dvsa|dvla|reddriving',
    'musical gear': r'feline guitars',
    'rehersal': r'mill hill music complex|pirate|the premises',
    'transfers in': r'bank credit',
    'education': r'hillel|course',
    'post office': r'post office',
    'personal transfers': r'^[a-z]{1,20} [a-z]{1,20}$',
    'number': r'^\d{1,10} ?\d{1,10}( [credit|withdrawal].*)?$',
    'toys': 'lego',
    'card': 'card|diy'
}


def get_category_from_entity(entity: str) -> str | None:
    for category, pattern in CATEGORY_REGEX.items():
        if re.search(pattern, entity.lower()):
            return category


categorised = defaultdict(list)
q = db_session.query(EnhancedTransaction)
res = q.all()
for r in res:
    categorised[get_category_from_entity(r.entity)].append(r.entity)
pp(categorised)
