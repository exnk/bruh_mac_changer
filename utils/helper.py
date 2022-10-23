import random
from utils.sql_client import SQLClient


def choice_random_vendor_mask():
    cli = SQLClient('identifier.sqlite')
    vendors = cli.get_vendors()
    selected = random.choice(vendors)[0]
    result = random.choice(cli.select_from_vendor(vendor_name=selected))
    if len(result[1]) > 6:
        result = choice_random_vendor_mask()
    return result[0], ':'.join([result[1]])
