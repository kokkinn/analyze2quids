import re


def get_cost_from_str(string: str) -> float:
    print(string)
    return float(re.search(r'\d+', string).group())
