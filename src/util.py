import re


def get_cost_from_str(string: str) -> float:
    return float(re.search(r'\d+', string).group())
