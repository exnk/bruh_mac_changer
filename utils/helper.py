from random import randint, choice

from utils.sql_client import SQLClient


DB: str = 'data.sqlite'


def choice_random_vendor_mask() -> tuple:
    cli = SQLClient(DB)
    vendors = cli.get_vendors()
    selected = choice(vendors)[0]
    result = choice(cli.select_from_vendor(vendor_name=selected))
    if len(result[1]) > 6:
        result = choice_random_vendor_mask()
    return result[0], result[1]


def get_vendor_mask(vendor: str) -> list:
    cli = SQLClient(DB)
    vendor = cli.select_from_vendor(vendor_name=vendor)
    if len(vendor) > 1:
        vendor = choice(vendor)
    return vendor


def generate_mac(mask: str) -> str:
    assert len(mask) == 6
    nums = ':'.join(map(lambda x: "%02x" % x, (randint(0x00, 0x7f), randint(0x00, 0xff), randint(0x00, 0xff))))
    return ':'.join([mask[0:2], mask[2:4], mask[4:], nums]).lower()
