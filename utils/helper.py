import random
from utils.sql_client import SQLClient
from random import randint


def choice_random_vendor_mask():
    cli = SQLClient('identifier.sqlite')
    vendors = cli.get_vendors()
    selected = random.choice(vendors)[0]
    result = random.choice(cli.select_from_vendor(vendor_name=selected))
    if len(result[1]) > 6:
        result = choice_random_vendor_mask()
    return result[0], result[1]


def generate_mac(mask: str) -> str:
    assert len(mask) == 6
    nums = ':'.join(map(lambda x: "%02x" % x, (randint(0x00, 0x7f), randint(0x00, 0xff), randint(0x00, 0xff))))
    return ':'.join([mask[0:2], mask[2:4], mask[4:], nums]).lower()


