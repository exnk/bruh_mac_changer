import copy
from jc import parse
from models.ifconfig_models import Ifmodel
from utils.interfaces import Interface
from rich.pretty import pretty_repr
import sys


class IFConfig:

    def __init__(self, raw: str) -> None:
        self.__raw: dict[str, Interface] = self.__normalize_to_models(raw)

    def __str__(self):
        return {k: v.__repr__() for k, v in self.__raw.items()}

    def __repr__(self):
        return {k: v.__repr__() for k, v in self.__raw.items()}

    def __getitem__(self, item):
        return self.__raw[item]

    @staticmethod
    def __normalize_to_models(raw: str) -> dict:
        data: list[dict] = parse('ifconfig', raw)
        result: dict[str, Interface] = {}
        for item in data:
            res = copy.deepcopy(item)
            tx = {k: res.pop(k) for k, v in item.items() if 'tx' in k}
            rx = {k: res.pop(k) for k, v in item.items() if 'rx' in k}
            ip4 = {k: res.pop(k) for k, v in item.items() if 'ipv4' in k}
            ip6 = {k: res.pop(k) for k, v in item.items() if 'ipv6' in k}
            res.update(dict(
                tx=tx,
                rx=rx,
                ip4=ip4,
                ip6=ip6
            ))
            model = Ifmodel(**res)
            interface = Interface(model)
            result.update({model.name: interface})
        return result

    def interface(self, interface: str) -> Interface:
        try:
            assert interface in self.__raw
        except AssertionError:
            sys.stdout.write(f"Error! Interface {interface} invalid!\nValid choices are% {' '.join(self.__raw)}")
        else:
            return self.__raw[interface]
